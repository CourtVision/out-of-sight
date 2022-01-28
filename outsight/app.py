import d6tflow
import logging
import argparse

logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# logging.error("Exception occurred", exc_info=True)

def main(name):
    print('Hello, %s!' % name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Say hello')
    parser.add_argument('name', default=1, help='your name, enter it')
    args = parser.parse_args()


# PDOC
# pdoc -o ./docs ./shelter.py
 """
    Given a URL, return the `requests` response object.

    Args:
        url (str): URL to scrape.

    Returns:
        requests.models.Response: `requests` response object.
"""



# get training data and save it
class GetData(d6tflow.tasks.TaskPqPandas):
    persist = ['x','y']

    def run(self):
        ds = sklearn.datasets.load_boston()
        df_trainX = pd.DataFrame(ds.data, columns=ds.feature_names)
        df_trainY = pd.DataFrame(ds.target, columns=['target'])
        self.save({'x': df_trainX, 'y': df_trainY}) # persist/cache training data


# train different models to compare
@d6tflow.requires(GetData)  # define dependency
class ModelTrain(d6tflow.tasks.TaskPickle):
    model = d6tflow.Parameter()  # parameter for model selection

    def run(self):
        df_trainX, df_trainY = self.inputLoad()  # quickly load input data

        if self.model=='ols':  # select model based on parameter
            model = sklearn.linear_model.LinearRegression()
        elif self.model=='gbm':
            model = sklearn.ensemble.GradientBoostingRegressor()

        # fit and save model with training score
        model.fit(df_trainX, df_trainY)
        self.save(model)  # persist/cache model
        self.saveMeta({'score': model.score(df_trainX, df_trainY)})  # save model score

# goal: compare performance of two models
# define workflow manager
flow = d6tflow.WorkflowMulti(ModelTrain, {'model1':{'model':'ols'}, 'model2':{'model':'gbm'}})
flow.reset_upstream(confirm=False) # DEMO ONLY: force re-run
flow.run()  # execute model training including all dependencies