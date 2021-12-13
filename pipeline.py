from google.cloud import aiplatform
import kfp
from kfp.v2 import dsl
from kfp.v2.dsl import *
from kfp.v2 import compiler
from kfp.v2.dsl import component

from get_data_component.src.task import ingest_comp

PROJECT_ID = None
LOCATION = None
PIPELINE_ROOT = None
SERVICE_ACCOUNT = None
EXPERIMENT = None

ingest_op = kfp.components.load_component('get_data_component/component.yaml')

'''
This is the lightweight component to reproduce in a standard component.
We want the keep the possibility to log metadata like in  `dataset_train.metadata['foo'] = 'bar'`
We also want to write the output using `dataset_train.path`
'''
@component(
    packages_to_install=[
        "pandas",
        "sklearn"
    ],
)
def get_data(
        dataset_train: Output[Dataset],
):
    from sklearn import datasets
    from sklearn.model_selection import train_test_split as tts
    import pandas as pd
    # import some data to play with
    print('PATH :' + dataset_train.path)
    print('URI :' + dataset_train.uri)

    data_raw = datasets.load_breast_cancer()
    data = pd.DataFrame(data_raw.data, columns=data_raw.feature_names)
    data["target"] = data_raw.target
    train, test = tts(data, test_size=0.3)

    dataset_train.metadata['foo'] = 'bar'
    train.to_csv(dataset_train.path)

@dsl.pipeline(
    pipeline_root=PIPELINE_ROOT,
)
def pipeline(
):
    get_data()
    ingest_op()


compiler.Compiler().compile(pipeline_func=pipeline,
                            package_path='pipeline.json')
# Submit a pipeline run

'''
This pipeline runs on Vertex AI
'''
aiplatform.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=PIPELINE_ROOT,
    experiment=EXPERIMENT
)

# Instantiate PipelineJob object
pl = aiplatform.PipelineJob(
    display_name="Example Project",
    enable_caching=True,
    template_path="pipeline.json",
    parameter_values={},
    pipeline_root=PIPELINE_ROOT,
)

# Submit the Pipeline to Vertex
pl.run(
    service_account=SERVICE_ACCOUNT,
    sync=True
)


