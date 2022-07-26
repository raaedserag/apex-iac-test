from azureml.pipeline.core import PublishedPipeline
from azureml.pipeline.core.schedule import ScheduleRecurrence, Schedule


def disable_existing_pipelines_and_schedules(aml_workspace, pipeline_name):
    published_pipelines = PublishedPipeline.list(aml_workspace)
    for published_pipeline in published_pipelines:
        if published_pipeline.name == pipeline_name:
            print(f"Disabling Pipeline: {published_pipeline.name},'{published_pipeline.id}'")
            # Disable all schedules within a pipeline
            schedules = Schedule.get_schedules_for_pipeline_id(aml_workspace, published_pipeline.id)
            for schedule in schedules:
                schedule.disable()
            # Disable pipeline
            published_pipeline.disable()


def schedule_pipeline(aml_workspace, published_pipeline, pipeline_name, experiment_name,
                      frequency, interval):

    disable_existing_pipelines_and_schedules(aml_workspace, pipeline_name)
    published_pipeline.enable()

    recurrence = ScheduleRecurrence(frequency=frequency, interval=interval)
    Schedule.create(aml_workspace, name="Recurrence schedule",
                    description="Scheduled Trigger",
                    pipeline_id=published_pipeline.id,
                    experiment_name=experiment_name,
                    recurrence=recurrence)
    print("Pipeline schedule initiated ")
