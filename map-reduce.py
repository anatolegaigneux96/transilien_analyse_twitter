import pandas as pd

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import AzureChatOpenAI
import operator
from typing import Annotated, List, Literal, TypedDict

from langchain.chains.combine_documents.reduce import (
    acollapse_docs,
    split_list_of_docs,
)
from langchain_core.documents import Document
from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from dotenv import load_dotenv
import asyncio
import pprint
from langchain_community.callbacks.manager import get_openai_callback

# Load environment variables
dotenv_path = ".env"
load_dotenv(dotenv_path=dotenv_path)  # Load Azure OpenAI environment variables

llm = AzureChatOpenAI(
    model_name="gpt-4o",
    deployment_name="gpt-4o",
    temperature=0.5,
)

map_prompt_name = "./prompts/map_prompt.md"
with open(map_prompt_name, "r") as file:
    map_prompt_str = file.read()

map_prompt_template = PromptTemplate(
    input_variables=[
        "tweet",
    ],
    template=map_prompt_str,
)


map_chain = map_prompt_template | llm | StrOutputParser()

reduce_prompt_name = "./prompts/reduce_prompt.md"
with open(reduce_prompt_name, "r") as file:
    reduce_prompt_str = file.read()

reduce_prompt_template = PromptTemplate(
    input_variables=[
        "summaries",
    ],
    template=reduce_prompt_str,
)
reduce_chain = reduce_prompt_template | llm | StrOutputParser()


token_max = 10000


def length_function(documents: List[Document]) -> int:
    """Get number of tokens for input contents."""
    return sum(llm.get_num_tokens(doc.page_content) for doc in documents)


# This will be the overall state of the main graph.
# It will contain the input document contents, corresponding
# summaries, and a final summary.
class OverallState(TypedDict):
    # Notice here we use the operator.add
    # This is because we want combine all the summaries we generate
    # from individual nodes back into one list - this is essentially
    # the "reduce" part
    contents: List[str]
    summaries: Annotated[list, operator.add]
    collapsed_summaries: List[Document]
    final_summary: str
    prompt_tokens: Annotated[int, operator.add]
    completion_tokens: Annotated[int, operator.add]
    total_tokens: Annotated[int, operator.add]


# This will be the state of the node that we will "map" all
# documents to in order to generate summaries
class SummaryState(TypedDict):
    content: str
    prompt_tokens: Annotated[int, operator.add]
    completion_tokens: Annotated[int, operator.add]
    total_tokens: Annotated[int, operator.add]


# Here we generate a summary, given a document
async def generate_summary(state: SummaryState):
    with get_openai_callback() as cb:
        response = await map_chain.ainvoke(state["content"])
    # Accumulate token usage
    return {
        "summaries": [response],
        "prompt_tokens": cb.prompt_tokens,
        "completion_tokens": cb.completion_tokens,
        "total_tokens": cb.total_tokens,
    }


# Here we define the logic to map out over the documents
# We will use this an edge in the graph
def map_summaries(state: OverallState):
    # We will return a list of `Send` objects
    # Each `Send` object consists of the name of a node in the graph
    # as well as the state to send to that node
    return [
        Send("generate_summary", {"content": content}) for content in state["contents"]
    ]


def collect_summaries(state: OverallState):
    return {
        "collapsed_summaries": [Document(summary) for summary in state["summaries"]]
    }


async def collapse_summaries(state: OverallState):
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_tokens = 0
    doc_lists = split_list_of_docs(
        state["collapsed_summaries"], length_function, token_max
    )
    results = []
    for doc_list in doc_lists:
        with get_openai_callback() as cb:
            result = await acollapse_docs(doc_list, reduce_chain.ainvoke)
        results.append(result)
        # Accumulate tokens from each call
        total_prompt_tokens += cb.prompt_tokens
        total_completion_tokens += cb.completion_tokens
        total_tokens += cb.total_tokens
    return {
        "collapsed_summaries": results,
        "prompt_tokens": total_prompt_tokens,
        "completion_tokens": total_completion_tokens,
        "total_tokens": total_tokens,
    }


# This represents a conditional edge in the graph that determines
# if we should collapse the summaries or not
def should_collapse(
    state: OverallState,
) -> Literal["collapse_summaries", "generate_final_summary"]:
    num_tokens = length_function(state["collapsed_summaries"])
    if num_tokens > token_max:
        return "collapse_summaries"
    else:
        return "generate_final_summary"


# Here we will generate the final summary
async def generate_final_summary(state: OverallState):
    with get_openai_callback() as cb:
        response = await reduce_chain.ainvoke(state["collapsed_summaries"])
    return {
        "final_summary": response,
        "prompt_tokens": cb.prompt_tokens,
        "completion_tokens": cb.completion_tokens,
        "total_tokens": cb.total_tokens,
    }


# Construct the graph
# Nodes:
graph = StateGraph(OverallState)
graph.add_node("generate_summary", generate_summary)
graph.add_node("collect_summaries", collect_summaries)
graph.add_node("collapse_summaries", collapse_summaries)
graph.add_node("generate_final_summary", generate_final_summary)

# Edges:
graph.add_conditional_edges(START, map_summaries, ["generate_summary"])
graph.add_edge("generate_summary", "collect_summaries")
graph.add_conditional_edges("collect_summaries", should_collapse)
graph.add_conditional_edges("collapse_summaries", should_collapse)
graph.add_edge("generate_final_summary", END)

app = graph.compile()


async def get_summary_report(tweets_df: pd.DataFrame):
    async for step in app.astream(
        {"contents": [row["combined"] for i, row in tweets_df.iterrows()]},
        {"recursion_limit": 10},
    ):
        print(step)

    # Access total token counts
    total_prompt_tokens = step.get("prompt_tokens", 0)
    total_completion_tokens = step.get("completion_tokens", 0)
    total_tokens = step.get("total_tokens", 0)
    print("Total Prompt Tokens:", total_prompt_tokens)
    print("Total Completion Tokens:", total_completion_tokens)
    print("Total Tokens:", total_tokens)
    return step["generate_final_summary"]["final_summary"]


if __name__ == "__main__":
    with open("graph.png", "wb") as f:
        f.write(app.get_graph().draw_mermaid_png())

    tweets_df = pd.read_excel("export-radarly-4625-documents-1732015114895.xlsx")

    tweets_df = tweets_df[["Date", "Text", "Title", "Lignes"]].head(100)

    # Concat the columns into 1 string that, combined column = "Date: <Date>; Text: <Text>; Title: <Title>; Lignes: <Lignes>"
    tweets_df["combined"] = tweets_df.apply(
        lambda row: f"Date: {row['Date']}; Tweet: {row['Text']}; Titre du Tweet: {row['Title']}; Lignes affectés: {row['Lignes']}",
        axis=1,
    )

    final_summary = asyncio.run(get_summary_report(tweets_df))
    # Dump the file
    with open("final_summary.txt", "w") as f:
        f.write(final_summary)
