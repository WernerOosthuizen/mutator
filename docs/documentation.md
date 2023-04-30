# Contents <!-- omit in toc -->

- [Introduction](#introduction)
- [Overview of functionality](#overview-of-functionality)
  - [Different forms of input tests](#different-forms-of-input-tests)
  - [Testing Example](#testing-example)
  - [Query parameter array formats](#query-parameter-array-formats)
  - [Fuzzing Request Bodies](#fuzzing-request-bodies)
  - [Analysis](#analysis)
  - [Custom Validators](#custom-validators)
  - [Default Validators](#default-validators)
  - [Reporting](#reporting)
  - [DRY RUN](#dry-run)
- [Configuration](#configuration)
  - [General Configuration](#general-configuration)
  - [Test Configuration](#test-configuration)
  - [Validator Configuration](#validator-configuration)
  - [Using a different database](#using-a-different-database)
  - [Worker Concurrency Settings](#worker-concurrency-settings)
  - [Test Runner Concurrency Settings](#test-runner-concurrency-settings)
  - [Environmental Variables](#environmental-variables)
  - [Custom Docker Volume Mounts](#custom-docker-volume-mounts)
- [Architecture overview](#architecture-overview)
  - [High level](#high-level)
  - [Worker Loop](#worker-loop)


## Introduction

Mutator is a minimalist API fuzzer, which aims to be easy to use and remove the toil of performing input testing for API's. The functionality can be accessed via a REST API.


## Overview of functionality
Mutator will pull apart an API call, replace or remove a value depending on the current test type, perform the API call, then perform a basic analysis of the response.
It will do this for each testable value in an API call. This can lead to a large amount of tests that are run in parallel. The progress can be monitored via the Mutator REST API and the concurrency levels can be adjusted as needed.

```
NOTE:  Headers are currently not fuzzed.
```

### Different forms of input tests
Mutator supports different input tests. Each test will replace the value under test with the relevant datatype and value.
The test types are configured here: src/mutator/config/test_config.json
- INTEGER
- STRING
- DOUBLE
- REMOVE

The "REMOVE" test type removes a field from the API call instead of replacing it with another value.
This is useful in flushing out issues when programs have required fields and do not perform adequate upfront validation.
See below for examples of the different test types.


### Testing Example
If the following request is received, it will be pulled apart and each field will be tested with various values in separate requests.

[See API Reference to create a test run.](./api-reference.md#create-a-test-run)  <!-- omit in toc -->

Received request that is to be tested:

GET https://www.testingthebestwebsite.com/this/website?and=parameter


Example of executed requests:
1. https://www.testingthebestwebsite.com/xxxxx/website?and=parameter
2. https://www.testingthebestwebsite.com/this/xxxxx?and=parameter
3. https://www.testingthebestwebsite.com/this/website?xxxxx=parameter
4. https://www.testingthebestwebsite.com/this/website?and=xxxxx


### Query parameter array formats
Two specific query parameter array formats are currently supported.

**?query=1,2,3,4**

An example of the request that is going to be fuzzed:
https://www.testingthebestwebsite.com/this/website?parameter=1,2,3,4

This will create the following fuzzing requests if the substitution value is "xxxxx":
1. https://www.testingthebestwebsite.com/this/website?xxxxx=1,2,3,4
2. https://www.testingthebestwebsite.com/this/website?parameter=xxxxx,2,3,4
3. https://www.testingthebestwebsite.com/this/website?parameter=1,xxxxx,3,4
4. https://www.testingthebestwebsite.com/this/website?parameter=1,2,xxxxx,4
5. https://www.testingthebestwebsite.com/this/website?parameter=1,2,3,xxxxx


**?query=1&query=2&query=3&query=4**

An example of the request that is to be fuzzed is:
?parameter=1&parameter=2&parameter=3&parameter=4

This will create the following fuzzing requests if the substitution value is "xxxxx":
1. https://www.testingthebestwebsite.com/this/website?xxxxx=1&parameter=2&parameter=3&parameter=4
2. https://www.testingthebestwebsite.com/this/website?parameter=xxxxx&parameter=2&parameter=3&parameter=4
3. https://www.testingthebestwebsite.com/this/website?parameter=1&xxxxx=2&parameter=3&parameter=4
4. https://www.testingthebestwebsite.com/this/website?parameter=1&parameter=xxxxx&parameter=3&parameter=4
5. https://www.testingthebestwebsite.com/this/website?parameter=1&parameter=2&xxxxx=3&parameter=4
6. https://www.testingthebestwebsite.com/this/website?parameter=1&parameter=2&parameter=xxxxx&parameter=4
7. https://www.testingthebestwebsite.com/this/website?parameter=1&parameter=2&parameter=3&xxxxx=4
8. https://www.testingthebestwebsite.com/this/website?parameter=1&parameter=2&parameter=3&parameter=xxxxx


### Fuzzing Request Bodies
Mutator can also be used to fuzz a request body (even if it contains nested information, which will be fuzzed recursively).
Each json field and value will be tested with various input values.

Example of body that is to be tested:
```
{
    "testing": "this",
    "body": [
        {
            "with": "nested",
            "values": "hello"
        }
    ]
}
```

Example Request 1
```
{
    "xxxxx": "this",
    "body": [
        {
            "with": "nested",
            "values": "hello"
        }
    ]
}
```

Example Request 2
```
{
    "testing": "xxxxx",
    "body": [
        {
            "with": "nested",
            "values": "hello"
        }
    ]
}
```

Example Request 3
```
{
    "testing": "this",
    "xxxxx": [
        {
            "with": "nested",
            "values": "hello"
        }
    ]
}
```

Example Request 4
```
{
    "testing": "this",
    "body": [
        {
            "xxxxx": "nested",
            "values": "hello"
        }
    ]
}
```

Example Request 5
```
{
    "testing": "this",
    "body": [
        {
            "with": "xxxxx",
            "values": "hello"
        }
    ]
}
```

Example Request 6
```
{
    "testing": "this",
    "body": [
        {
            "with": "nested",
            "xxxxx": "hello"
        }
    ]
}
```

Example Request 7
```
{
    "testing": "this",
    "body": [
        {
            "with": "nested",
            "values": "xxxxx"
        }
    ]
}
```

### Analysis
Each response is analysed using validators found in `src/mutator/result_processor/validations` and a `passed` boolean value is set on the validation result along with a custom message explaining the outcome of the validation.

If any validator fails, it will result in a test run failure.

### Custom Validators
Custom validators are easy to add and are automatically imported. They need to be located in the `src/mutator/result_processor/validations` folder, and must inherit from class `src.mutator.result_processor.validations.validator.Validator`.

The `src.common.test_result.test_result.TestResult` object will be available for use in the validator.

If custom configuration is required, a dictionary object will also be injected (see `src.mutator.result_processor.service.result_processor_service.get_enabled_validators`) if it is configured in `src/mutator/config/validator_config.json`, or sent in as part of the request object. e.g.

```
{
    "endpoint": {
        "method": "POST",
        "headers": {
            "Content-Type": "application/json"
        },
        "url": "http://localhost:8010/v1/results",
        "body": {
            "modifiers": [
                1,
                2,
                3,
                4,
                5,
                6,
                7
            ]
        }
    },
    "config": {
        "validation": {
            "StatusCode": {
                "enabled": false,
                "invalid_status_codes": [
                    500
                ]
            },
            "ElapsedTime": {
                "enabled": true,
                "max_elapsed_time": 0.001
            }
        }
    }
}
```
NB: The json key in the validator config must match the validator class name exactly.

If an `enabled` flag is not set a validator will be run by default if it is found.

### Default Validators
- Invalid status codes: Will fail if any status code larger than or equal to 500 is found. A custom list of status codes can be supplied.
- Elapsed time: If the test elapsed time is larger than specified time, the validation will fail.
- StringMatch: If the specific string is found in the response, the validation will fail.
- Regression: If a request has been run before (identified by a request hash), the current response hash will be compared to the previous response hash.

Due to the fact that the `Regression` validator needs some custom configuration based on each API call, it is disabled by default and must be enabled in the validator configuration (`src/mutator/config/validator_config.json`).

If the `Regression` validator is enabled, it will create a response hash for every response received. A response might have dynamic fields (such as a date) which would affect the final hash value, so there are various "strategies" that can be selected to create the response hash. Each strategy affects which field names and values are used to create a response hash.  If the fields are configured correctly, you will consistently get the same response hash for this response every time the test is run. This will allow us to validate that the core data in the API response is always the same.

Hash creation strategies
```
ALL: Include all fields in response hash.
INCLUDE_EXACT_MATCH: Include specific fields in response hash. Needs to be an exact match.
EXCLUDE_EXACT_MATCH: Exclude specific fields from response hash. Needs to be an exact match.
EXCLUDE_PARTIAL_MATCH: Exclude fields from response hash. Can be a partial match.
```

Example:

```
{
    "id": 1234,
    "name": "Bob",
    "surname": "Smith",
    "create_date": "2222-10-24T00:00:00"
}
```
For strategy `INCLUDE_EXACT_MATCH` the exact fields that must be used to create the hash must be specified. If 'name,surname' is configured only those two fields will be used to create the hash.

For strategy `EXCLUDE_PARTIAL_MATCH` if 'id,date' is configured (the default example configuration), the fields 'id' and 'create_date' will be matched and excluded from the response hash generation. Only 'name' and 'surname' will be matched.

For strategy `EXCLUDE_EXACT_MATCH` if 'date' is configured, 'create_date' will NOT be matched. 'create_date' must be configured as an exact match.

If the response hash between two responses (identified by the request hash) are different the test will be set as not passing the regression validation.


### Reporting

[See API Reference for test run reports.](./api-reference.md#get-test-run-reports)

```
NOTE:  There is little validation performed on this endpoint to allow for easy customisation of reports. You might get errors if your queries are not written correctly, or if ALL of your parameters are not passed to the API. An detailed error message should be seen in the response if this happens.
```

Reports can be run to gain further insights into the outcome of a test run. The reporting endpoint runs plain paramaterised SQL statements that can be expanded on as needed.

For now these live in a JSON file at `src/manager/config/reports.json`, so that they are easy to expand on and customise. If you wish to add your own reports to run, just add a report handle as the key, and the paramaterised sql as the value.

e.g. "test_result_by_test_value_for_type": "select test_run_id, test_value, passed, count(id) as count from test_result where test_type = :test_type group by 1,2,3;"

When running an API call to execute this report and you need to pass parameters (such as `test_type` in this example), they can be passed as query parameters, and it would look as follows:

```
curl --request GET --url http://localhost:8000/v1/reports/test_result_by_test_value_for_type?test_type=INTEGER
```

The results can be output as CSV files if the following query parameter is added: `format=csv`


### DRY RUN
Adding the environmental flag "DRY_RUN" will log the tests that are generated and not run them. This can be useful to see what will be run before committing to an actual test run against a service.


## Configuration
### General Configuration
The default configuration should be good enough to get you started. There are however some configs that can be updated.

There are three general configuration files.

Common: `src/common/config/logging.ini`
Manager: `src/manager/config/config.ini`
Mutator: `src/mutator/config/config.ini`

### Test Configuration
You can specify which test types (INTEGER, STRING, DOUBLE, REMOVE) must be run by including them in `src/mutator/config/test_config.json`

### Validator Configuration
You can specify configuration that will be injected into each validator: `src/mutator/config/validator_config.json`

NB: The json key in the validator config must match the validator class name exactly.

### Using a different database
By default Sqlite is used so that you don't have to set up a database. If you would prefer to use a separate DB the easiest option would be to set the connection string as the "DATABASE" environment variable:

Using Docker it can be done by setting the environment variable: -e DATABASE={DB_USER}:{DB_PASSWORD}@{DB_URL}:{DB_PORT}.

You will also have to add the required driver. E.g. adding mysql driver:

run: `poetry add pymysql`

Then use the connection string: `mysql+pymysql://user:password@db:3306/mutator`

```
docker run \
-d \
-e DATABASE=mysql+pymysql://user:password@db:3306/mutator
-p 80:8000 \
-v /home/user/Documents/data_dir_here/database:/app/data/database \
mutator
```


Theoretically everything should work fine as long as it is supported by Sqlalchemy.
List of supported Sqlalchemy databases can be found here: https://docs.sqlalchemy.org/en/latest/dialects/index.html


### Worker Concurrency Settings
The amount of background workers are currently locked to the CPU count, up to a maximum of 6. Not currently configurable.

### Test Runner Concurrency Settings
In the mutator general config file (`src/mutator/config/config.ini`) you will find the "count" value under the "consumer" section. This sets the concurrent threads that will perform the test requests, and analyse the results.

### Environmental Variables
Use a different database. Keep in mind that the library (pymysql in this example) has to be installed as a dependency.
`DATABASE=mysql+pymysql://app:password@localhost:3306/mutator`

Hose and port values to bind to at startup.
`HOST=0.0.0.0`
`PORT=8000`

### Custom Docker Volume Mounts
Mount custom test seed value files that can be easily updated. The other option would be to update them in the source code and rebuild the docker file.
`/home/user/Documents/mutator_data/test_repository:/app/src/mutator/config/test_repository`

Example to mount the Sqlite DB file in an accessable folder
`/home/user/Documents/mutator_data/database:/app/data/database`


## Architecture overview
### High level
```
                                    ┌────────────────────────────────────────────────────────────────────────┐
                                    │                                   MUTATOR                              │
                                    │                                                                        │
                                    │      ┌─────────────┐          ┌────────────────────────┐               │
                                    │      │   MANAGER   │          │                        │               │
                                    │      │             │          │  MUTATOR WORKER LOOP   │               │
                                    │      │  API LAYER  │          │                        │               │
                                    │      │             │          │                        │               │
  ┌─────────────┐                   │      │             │          │                        │               │               ┌─────────────┐
  │             │                   │      │             │          │                        │               │               │    SERVER   │
  │    USER     │                   │      └──────┬──────┘          └───────────┬────────────┘               │ ───────────►  │             │
  │             │ CREATE TEST RUN   │             │                             │                            │               │             │
  │             │                   │             │                             │                            │               │             │
  │             │   ──────────►     │             │                             │ FETCH TEST FROM DATABASE   │               │             │
  │             │                   │             │   PERSIST TEST RUN IN DB    │ RUN AND ANALYSE RESULTS    │               │             │
  │             │                   │             │                             │ PERSIST TEST RESULTS       │               │             │
  │             │                   │             │                             │                            │               │             │
  │             │                   │             │                             │                            │               │             │
  │             │                   │             │                             │                            │               │             │
  │             │                   │             │                             │                            │               │             │
  │             │   ◄──────────     │             │                             │                            │ ◄───────────  │             │
  │             │                   │             │                             │                            │               │             │
  │             │                   │             │                             │                            │               │             │
  │             │                   │    ┌────────▼─────────────────────────────▼────────────────────────┐   │               └─────────────┘
  │             │                   │    │                  DATABASE                                     │   │
  └─────────────┘                   │    │                                                               │   │
                                    │    │                                                               │   │
                                    │    │                                                               │   │
                                    │    │                                                               │   │
                                    │    └───────────────────────────────────────────────────────────────┘   │
                                    │                                                                        │
                                    └────────────────────────────────────────────────────────────────────────┘
```

### Worker Loop
```
 ┌────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                                          WORKER LOOP                                           │
 │                                                                            ┌────────────────┐  │
 │                                                                            │CONSUMER 1      │  │
 │                                                                            │-RUN TEST       │  │
 │                                                                        ┌──►│-ANALYSE RESULT │  │
 │                                                                        │   └────────────────┘  │
 │                                                                        │                       │
 │   ┌─────────────┐       ┌─────────┐     ┌──────────┐       ┌────────┐  │                       │
 │   │  GENERATOR  │       │QUEUE    │     │QUEUE     │       │MEMORY  │  │                       │
 │   │             │       │WRITER   │     │READER    │       │QUEUE   │  │   ┌────────────────┐  │
 │   │ - CREATE    │       |-BATCH   │     │-THROTTLE │       │        │  │   │CONSUMER 2      │  │
 │   │   TESTS     ├─────► │ WRITE   ├────►│-TRACK    ├─────► │-THREAD ├──┼──►│-RUN TEST       │  │
 │   │ - GET TOTAL │       │ TO      │     │ PROGRESS │       │ SAFE   │  │   │-ANALYSE RESULT │  │
 │   │   TEST COUNT│       │ DISK    │     │          │       │        │  │   └────────────────┘  │
 │   │             │       │ QUEUE   │     │          │       │        │  │                       │
 │   └─────────────┘       └─────────┘     └──────────┘       └────────┘  │                       │
 │                                                                        │                       │
 │                                                                        │   ┌────────────────┐  │
 │                                                                        │   │CONSUMER N      │  │
 │                                                                        └──►│-RUN TEST       │  │
 │                                                                            │-ANALYSE RESULT │  │
 │                                                                            └────────────────┘  │
 │                                                                                                │
 └────────────────────────────────────────────────────────────────────────────────────────────────┘

```
