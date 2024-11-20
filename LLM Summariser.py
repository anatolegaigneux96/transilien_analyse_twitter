# import os
# import yaml
# import argparse
# import json
# from langchain_openai import AzureChatOpenAI
# from langchain_core.prompts import (
#     PromptTemplate,
# )
# from dotenv import load_dotenv
# from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
# import pandas as pd
# from datetime import datetime
# import sys


# def map(input_vars):
#     print("-----Running map: summarising batches of tweets ------")

#     # Load environment variables
#     dotenv_path = ".env"
#     load_dotenv(dotenv_path=dotenv_path)  # Load Azure OpenAI environment variables

#     llm = AzureChatOpenAI(
#         deployment_name="gpt-4o",
#         temperature=0.5,
#     )

#     prompt_file_name = "./map_prompt.md"
#     with open(prompt_file_name, "r") as file:
#         prompt_str = file.read()

#     prompt_template = PromptTemplate(
#         input_variables=[
#             "tweet",
#         ],
#         template=prompt_str,
#     )

#     map_summary_chain = prompt_template | llm | StrOutputParser()

#     summary = map_summary_chain.batch(input_vars, config={"max_concurrency": 50})

#     print("-----Done-----")
#     return summary


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Summarise tweets using LLM")
#     parser.add_argument(
#         "--limit",
#         type=int,
#         default=None,
#         help="Number of tweets to summarise. Default is None",
#     )

#     args = parser.parse_args()

#     # Load the YAML file
#     with open("./loaders/instructions/cefr_level_descriptors.yaml", "r") as file:
#         CEFR_level_descriptors = yaml.safe_load(file)

#     # Load the tweets
#     tweets_df = pd.read_excel("tweets.xlsx")

#     input_vars_list = []
#     for i, row in tweets_df.iterrows():
#         input_vars = {
#             "version": args.version,
#             "target_language": args.target_language,
#             "platform_language": args.platform_language,
#             "chapter_number": int(row["Chapter Number"]),
#             "CEFR_level": row["CEFR Sublevel"],
#             "CEFR_level_descriptor": CEFR_level_descriptors[row["CEFR Level"]],
#             "chapter_category": row["Category"],
#             "chapter_title": row["Chapter Title"],
#             "associated_chapters": row["Associated Chapters"],
#             "created_at": datetime.now().replace(microsecond=0).isoformat(),
#         }
#         input_vars_list.append(input_vars)
#     print(f"Sending batch of {len(input_vars_list)} to OpenAI API")
#     main(input_vars_list)
