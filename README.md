# NBA MVP Prediction App

This repository contains the code generated for running an application which deploys machine learning models to predict the NBA MVP award winner of the current season. 

Anybody who wants to check the NBA MVP Prediction Web App can test it navigating to the next link: [nba-mvp-prediction.xyz](https://nba-mvp-prediction.xyz). 

The app is currently in an initial phase and it will be updated regularly during the next months.

## App Structure

The following diagram shows the structure of the app:

![app-diagram](/readme-pics/app_diagram.png)

It is mainly composed by two systems which are in charge of two distinct tasks in the app: the data updater and the results visualizer.

## Data Updater

Every day at 10:00 UTC, an *AWS Lambda* function is triggered through an *AWS Event Bridge* cronjob and executes the following actions:

1. Webscraping is used to extract individual stats (both standard and advanced) from each NBA player from [Basketball Reference](https://www.basketball-reference.com). To do that, the function uses a custom module (named basketball_reference_rodrixx) created to extract the stats from the website using *BeautifulSoup4* library. This same module does also some data cleaning and parses the information into a DataFrame.
2. The stats are pre-procesed so that the ML models can ingest them. This is achieved using a *Scikit-Learn* pipeline and several custom transformers defined in a custom module (named preprocessing_lib_rodrixx). The pipeline drops player rows which are repeated because of a team switch during the leage, sets indexes, encodes categorical data and drops some columns.
3. The processed stats are passed to the ML models and the MVP results are predicted. The models in pickle format are saved in an *AWS S3* bucket, so that the lambda function can load them in the execution process. These models are explained in more detail in [this section](#ml-models)
4. The output of the model is post-processed in order to extract additional metrics (votes, adjusted share and rank), and also deleted columns that were not used by the model are added again to the dataset. Column names are formatted so that the database can handle them. A custom module is used for this part of the process (named postprocessing_lib_rodrixx).
5. Post-processed data is finally appended to the corresponding PostgreSQL table using the *SQLalchemy* module.

This *AWS Lambda* function code is implemented in Python as a container image. The repo containing the code and Dockerfile to deploy the container image can be found [here](https://github.com/Rodrixx05/nba-mvp-prediction-lambda). The image is uploaded to *AWS Elastic Container Registry* so that *AWS Lambda* can run it every time the function is triggered.

### ML Models

The 3 machine learning models that are currently used by the app are based on the following methods:

- **Random Forest Regressor**: it combines the output of multiple decision trees to reach a single result.
- **XGBoost Regressor**: it implements the gradient boosting algorithm, adding one decision tree at a time to the ensemble and fit to correct the prediction errors made by prior models.
- **Ensemble Regressor**: it combines both previous methods using a voting regressor to obtain the final result.

All the models have been trained using individual stats (both standard and advanced stats) as predictors and the MVP voting share as the target, from the seasons between years 1982 and 2015. They have also been validated using data from seasons between 2015 and 2022. 

The output of the models is served in 4 different forms:

- **Predicted Share**: it's the percentage of votes received over the maximum votes a player can get. It's the target of the ML models, and it can be considered the "raw output" as no restrictions are applied in terms of total votes given. So if this perecentage was multiplied for the maximum number of votes a player can receive for each player and a summation was applied, the total number of votes awarded for all the players can be unrealistic. 
- **Predicted Votes**: it's the number of votes each player receives considering the predicted share. To avoid the issue presented in the above metric, the maximum number of votes a player can receive is taken into account (currently 1010, and it can be adjusted through a function in the postprocessing module). It then assumes that there will only be 17 contenders with votes from the jury (average value from the past seasons), so votes are distributed among the 17 players with best voting share, using their predicted share as the wheight of the distribution.
- **Adjusted Predicted Share**: using the predicted votes calculated in the above metric, the predicted share is adjusted considering the maximum number of votes a player can get.
- **Predicted Rank**: it simply ranks all the players using the predicted share.

Data was also extracted from [Basketball Reference](https://www.basketball-reference.com) using the same custom module mentioned in [this section](#data-updater). The tracking of all the experiments' parameters and results have been done with MLFlow. The notebooks containing the modelling work done can be found in this [repo](https://github.com/Rodrixx05/nba-mvp-prediction-modelling).

In the future, a significant improvement is expected to be applied to the models. The idea is to take into account how the panel votes for the players. Each member votes 5 players with the following votes scoring:
- 10 points to the first place player
- 7 points to the second place player
- 5 points to the third place player
- 3 points to the fourth place player
- 1 point to the fifth place player

Once the predicted share is obtained, an experiment would be run for each member of the panel to check which 5 players are chosen, using the predicted share of the players as the weighted probability. 

## Results Visualizer

This part of the app is meant to be working 24/7 so that anyone who wants to check the results of the app can do it. For this reason, all the services created for the results visualizer are deployed in an *AWS EC2* server which is online continuously. *Docker-compose* is used to run and connect the different services shown in the above [diagram](#app-structure). The compose file deployed in production can be found [here](docker-compose-prod.yml).

The services deployed in the docker-compose cluster are briefly explained in the next list:

1. **Database**: a *PostgreSQL* database is used to store the daily stats and prediction results that are collected by the *AWS Lambda* function. 
2. **Interactive web app + WSGI**: a dashboard with graphs and tables is created using mainly *Dash* and *Plotly* libraries. These modules have the ability to build both the back-end and the front-end of the app with Python code. The web app queries the data requested by the user from the database using the *SQLalchemy* module, and the queries are refreshed every time the user changes and interactive component of the interface. In order to enable the communication of the Python web app with the web server, a WSGI (Web Server Gateway Interface) is implemented using *Gunicorn*. Both the web app and the WSGI are deployed as a unique service using the custom container image named dash-app, and it can be found in this [folder](dash-files/) of the repository.
3. **Web server**: an *Nginx* reverse proxy listens to HTTP requests on port 80 and redirects them to the web app content through the WSGI. A custom Nginx image has been developed for this purpose, and it can be found in this [folder](nginx-files/)
4. **SSL certificate provider**: in order to enable secure HTTPS requests to the app, a *Certbot* service is in charge to obtain the SSL certificate for encrypted connections. Once a month, a cronjob is triggered in the *AWS EC2* server which re-launches the certbot service to renew the certificate.

### Web App Description

The next picture shows the app's interface:

![app-diagram](/readme-pics/web_app.png)

The app is currently composed of 4 different sections where the user can introduce the desired configuration:

1. **Initial Configuration**: The user can choose to either display data from the best players at the moment (introducing the amount of players) or he can specify which players have to be visualized. The ML model also needs to be selected (each of them are explained in [this section](#ml-models)). Once these parameters are fixed, they are going to determine which players and models results are represented in the subsequent sections. If one of the parameters is modified, the data from the graphs and tables of the app is automatically updated.

2. **MVP Score Timeseries**: Timeseries graph where the selected model results are displayed through the avaiable period of time. The user can set the desired interval and the model output type. This way, one can easily see the evolution of the players' performance during the season.

3. **Models comparator**: Table where the user selects an output type, and the results for each model are compared, highlighting which models haver better or worse scores for each player. With this section, the user can verify if a player performs similarly in all the models (thus, considering the results reliable) or if one score might be an outlier. 

4. **Stats comparator**: Table where, initially, only the predicted share and predicted votes are displayed. With the dropdown below the table, the user can add a column for each stat he chooses. The aim of this table is to visually check if a specific stat has a big or low influence on the model output. 