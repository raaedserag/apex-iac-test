from azure.identity import DefaultAzureCredential
from azure.eventgrid import EventGridPublisherClient, EventGridEvent


def send_event(data, subject, event_type, data_version, endpoint):
    """
    Send notifications and events to Even Grid. 

    Leverages Managed identities for authorization. This requires
    the Service Principal of the compute that runs the training or 
    monitoring pipelines to have permissions to post events to the 
    Event Grid instance.
    """
    event = EventGridEvent(
        data=data,
        subject=subject,
        event_type=event_type,
        data_version=data_version
    )

    # Default credentials, should work within the pipeline run
    credential = DefaultAzureCredential()

    client = EventGridPublisherClient(endpoint, credential)

    client.send(event)
    print("Sending event")
    print(event)
    client.close()
