import requests
from typing import Any, List, Optional
from pydantic import BaseModel, Field, RootModel
from collections import Counter, defaultdict

class ValueField(BaseModel):
    name: str
    type: str
    value: Any

class DecodedDataItem(BaseModel):
    name: str
    type: str
    signature: str
    value: ValueField

DecodedDataItems = RootModel[List[DecodedDataItem]]

class Attestation(BaseModel):
    attester: str
    recipient: str
    decodedDataJson: str

class Schema(BaseModel):
    attestations: List[Attestation]

class QueryResponse(BaseModel):
    data: Optional[dict]
    errors: Optional[List[dict]]

class Data(BaseModel):
    schema_: Schema = Field(..., alias='schema')

class GraphQLResponse(BaseModel):
    data: Data

def query_graphql():
    url = 'https://base.easscan.org/graphql'
    
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Origin': 'https://studio.apollographql.com',
        'Referer': 'https://studio.apollographql.com/sandbox/explorer',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'content-type': 'application/json'
    }
    
    query = """
    query {
      schema(where: {id: "0x080a79410f9c625106db1bd1bd2b83cf2b04b42598d3ec338635c4827692f72f"}) {
        attestations {
          attester
          recipient
          decodedDataJson
        }
      }
    }
    """
    
    data = {
        'query': query
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Lanza una excepción si hay un error HTTP
        
        ctr = defaultdict(set)  # Utiliza un conjunto para contar atestaciones únicas
        result = response.json()
        graphql_response = GraphQLResponse(**result)

        for attestation in graphql_response.data.schema_.attestations:
            if attestation.attester.lower() != '0xd5064bd244138fa4ff1b9048d165491889af5c15':
                continue

            decoded = DecodedDataItems.model_validate_json(attestation.decodedDataJson)
            for item in decoded.root:
                if item.name == 'offering':
                    ctr[attestation.recipient].add(item.value.value)

        # Convertir el conjunto a una lista de tuplas y ordenar por el tamaño del conjunto (número de atestaciones únicas)
        ranking = sorted([(wallet, len(offerings)) for wallet, offerings in ctr.items()], key=lambda x: x[1], reverse=True)
        # Imprimir el ranking
        sortedList = []
        for rank, (wallet, count) in enumerate(ranking, start=1):
            sortedList.append([rank,wallet,count])
            print(f"Rank {rank}: Billetera: {wallet}, Atestaciones Únicas: {count}")
        return sortedList

    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")

    except Exception as e:
        print(f"Error occurred: {e}")