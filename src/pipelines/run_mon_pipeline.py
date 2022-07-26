from azureml.pipeline.core import PublishedPipeline
from azureml.core import Experiment, Workspace
import argparse
from aml_services.utils.env_variables import Env
from azureml.pipeline.core.schedule import ScheduleRecurrence, Schedule

def main():

    parser = argparse.ArgumentParser("register")
    parser.add_argument(
        "--output_pipeline_id_file",
        type=str,
        default="pipeline_id.txt",
        help="Name of a file to write pipeline ID to"
    )
    parser.add_argument(
        "--skip_mon_schedule",
        action="store_true",
        help=("Do not schedule the pipeline. "
              "Use this in Azure DevOps when using a server job to trigger")
    )
    args = parser.parse_args()

    e = Env()

    aml_workspace = Workspace.get(
        name=e.workspace_name,
        subscription_id=e.subscription_id,
        resource_group=e.resource_group
    )

    # Find the pipeline that was published by the specified build ID
    pipelines = PublishedPipeline.list(aml_workspace)
    matched_pipes = []
    matched_cur_pipes = []

    #Disable current schdules
    for p in pipelines:
        if p.name == e.monitor_pipeline_name:
            matched_cur_pipes.append(p)
     
    if(len(matched_cur_pipes) > 1):   
        published_cur_pipeline = None
    else:
        for cur_pipelines in matched_cur_pipes:
          if(Schedule.get_schedules_for_pipeline_id(cur_pipelines.id)):
            Schedule.disable(cur_pipelines.id)        

    #Disable current schdules
    for p in pipelines:
        if p.name == e.monitor_pipeline_name:
            matched_cur_pipes.append(p)
     
    if(len(matched_cur_pipes) > 1):   
        published_cur_pipeline = None
    else:
        for cur_pipelines in matched_cur_pipes:
          if(Schedule.get_schedules_for_pipeline_id(cur_pipelines.id)):
            Schedule.disable(cur_pipelines.id)        

    for p in pipelines:
        if p.name == e.monitor_pipeline_name:
            if p.version == e.build_id:
                matched_pipes.append(p)

    if(len(matched_pipes) > 1):
        published_pipeline = None
        raise Exception(f"Multiple active pipelines are published for build {e.build_id}.")  # NOQA: E501
    elif(len(matched_pipes) == 0):
        published_pipeline = None
        raise KeyError(f"Unable to find a published pipeline for this build {e.build_id}")  # NOQA: E501
    else:
        published_pipeline = matched_pipes[0]
        print("published pipeline id is", published_pipeline.id)

        # Save the Pipeline ID for other AzDO jobs after script is complete
        if args.output_pipeline_id_file is not None:
            with open(args.output_pipeline_id_file, "w") as out_file:
                out_file.write(published_pipeline.id)

        if(args.skip_mon_schedule is False):
            pipeline_parameters = {"model_name": e.model_name}
            tags = {"BuildId": e.build_id}
            if (e.build_uri is not None):
                tags["BuildUri"] = e.build_uri
            experiment = Experiment(
                workspace=aml_workspace,
                name=e.experiment_name)
            recurrence = ScheduleRecurrence(frequency="Day", interval=2)
            recurring_schedule = Schedule.create(aml_workspace, name="MyRecurringSchedule", 
                            description="Based on time",
                            pipeline_id=published_pipeline.id,
                            experiment_name=e.experiment_name, 
                            recurrence=recurrence)
            print("Pipeline schedule initiated ")


if __name__ == "__main__":
    main()
