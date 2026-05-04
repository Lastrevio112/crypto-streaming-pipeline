import requests
import json

""" This function can be called for each individual data source to register or update a schema in the registry. 
    Compatibility should be forward by default to ensure that if the API/websocket adds fields in the future, it will not break our pipeline."""
def register_schema(
        schema_registry_url : str, 
        subject : str, 
        schema : dict, 
        schema_type: str = "AVRO", 
        compatibility: str | None = "FORWARD"
) -> int:
    # Set compatibility to FORWARD - if the API/websockets add fields in the future, it will not break our pipeline
    if compatibility:
        requests.put(
            f"{schema_registry_url}/config/{subject}",
            json={"compatibility": compatibility}
        ).raise_for_status()

    # Register the schema in the registry
    response = requests.post(
        f"{schema_registry_url}/subjects/{subject}/versions",
        json={
            "schema": json.dumps(schema),
            "schemaType": schema_type
        },
        headers={"Content-Type": "application/vnd.schemaregistry.v1+json"}
    )

    response.raise_for_status()
    print(response.json())

    return response.json()["id"]  # int