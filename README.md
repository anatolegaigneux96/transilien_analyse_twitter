# Transilien Voix du Client

Transilien Voix du Client is a project aimed at analyzing and summarizing customer tweets to enhance the traveler experience. By leveraging natural language processing, the project identifies key insights from customer feedback to help Transilien improve its services.

## Installation
1. **Create virtual env**
```
python -m venv venv
```
2. **Activate virtual env**
On Windows:
```
venv\Scripts\activate
```

On Unix:
```
source venv/bin/activate
```

3. **Dependencies**
```
pip install -r requirements.txt
```

4. **Configuration**
Create a .env file in the root directory with your Azure OpenAI API credentials:

```
OPENAI_API_VERSION=2023-12-01-preview
AZURE_OPENAI_ENDPOINT=<your_azure_openai_endpoint>
AZURE_OPENAI_API_KEY=<your_api_key>
```

## Usage

1. Prepare data
Place the Excel file containing th RADARLY export in the root directory

2. Run the script
Run the map-reduce.py script to analyze tweets:
```
python map-reduce.py
```
