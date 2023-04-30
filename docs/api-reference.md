# Contents <!-- omit in toc -->

- [Request and Response formatting](#request-and-response-formatting)
- [Pagination](#pagination)
- [Sorting](#sorting)
- [Versioning](#versioning)
- [Resources](#resources)
	- [Test Runs](#test-runs)
		- [Create a test run](#create-a-test-run)
		- [Batch create test runs](#batch-create-test-runs)
		- [Stop a Test Run](#stop-a-test-run)
		- [Get all test runs](#get-all-test-runs)
		- [Get Specific Test Run](#get-specific-test-run)
	- [Test Results](#test-results)
		- [Test Result Object](#test-result-object)
		- [Get test results](#get-test-results)
		- [Get specific test results](#get-specific-test-results)
		- [Get test results across all test runs](#get-test-results-across-all-test-runs)
		- [Get test run reports](#get-test-run-reports)
		- [Run a specific test run report](#run-a-specific-test-run-report)

<br/>

# Request and Response formatting
The requests accept JSON-encoded bodies and also return JSON-encoded bodies.

Standard HTTP methods and response codes are used where applicable.


# Pagination
The API's support pagination. The default Maximum page size is 50 if a value is not specified.

e.g:
```
curl --request GET --url 'http://localhost/v1/testruns?page=3&page_size=30'
```

**Parameters**

**page: Integer**

The page number for the API response.
```
Constraints
- Minimum size: 0
- Maximum size: 65000
```

**page_size: Integer**

The amount of items that should be in the response.
```
Constraints
- Minimum size: 0
- Maximum size: 50
```
<br/>

# Sorting
The API's support ordering based on entry creation time. The query parameter is called "sort_order", and the allowed values are: "asc", "ASC", "desc", "DESC".
e.g:
```
curl --request GET --url 'http://localhost/v1/testruns?sort_order=desc'
```

# Versioning
The API's use a path based versioning scheme. The version will increment on any breaking changes.

<br/>

# Resources
## Test Runs

### Create a test run
Create a test run to fuzz an API.

**Endpoint Parameters**

**method: String**

The http method that will be used.
```
Constraints
- Required
- Allowed values: "GET", "POST", "PUT", "DELETE", "PATCH".
```

**headers: JSON**

The headers for the http request consist of a JSON structure. The headers are not fuzzed.
```
Constraints
- Required
```

**url: String**

The url that is to be tested.
```
Constraints
- Required
- Supported protocols: "http", "https".
```

**body: JSON**

The body that is to be tested.
```
Constraints
- Optional
```

**Request Example**
```
curl --request POST \
  --url http://localhost/v1/testruns \
  --header 'Content-Type: application/json' \
  --data '{
	"endpoint": {
		"method": "POST",
		"headers": {
			"Content-Type": "application/json"
		},
		"url": "http://test-app:8010/endpoint/being/tested",
		"body": {
			"lets": "test",
			"the": 1234,
			"endpoint": {
					"testing": "endpoint"
			}
		}
	}
}
'
```

**Response Example**
```
{
	"id": 1111111,
	"endpoint": {
		"method": "POST",
		"headers": {
			"Content-Type": "application/json"
		},
		"url": "http://test-app:8010/endpoint/being/tested",
		"body": {
			"the": 1234,
			"lets": "test",
			"endpoint": {
				"testing": "endpoint"
			}
		}
	},
	"config": null,
	"batch_id": null,
	"state": "PENDING",
	"state_description": "The test run is queued for processing.",
	"passed": null,
	"test_generated_count": null,
	"test_result_count": null,
	"run_attempts": 1,
	"create_date": "2222-01-01T00:00:00",
	"last_update_date": "2222-01-01T00:00:00"
}
```

### Batch create test runs
Batch create test runs to fuzz an API.

**Parameters**

**common: JSON**

The common configuration that will be applied to every test run in the batch, such as headers. Headers will be merged with the other configured headers in each test run config.
```
Constraints
- Optional
```

**endpoints: Array[Endpoints]**
The list of endpoints that will be used to create multiple test runs. This is a list of requests similar to #create-a-test-run.

```
Constraints
- Required
- Minimum size: 1
- Maximum size: 100
```

**Endpoint Parameters**

**method: String**

The http method that will be used.
```
Constraints
- Required
- Allowed values: "GET", "POST", "PUT", "DELETE".
```

**headers: JSON**

The headers for the http request consist of a JSON structure. The headers are not fuzzed.
```
Constraints
- Required
```

**url: String**

The url that is to be tested.
```
Constraints
- Required
- Supported protocols: "http", "https".
```

**body: JSON**

The body that is to be tested.
```
Constraints
- Optional
```

**Request Example**
```
curl --request POST \
  --url http://localhost/v1/batch/testruns \
    --header 'Content-Type: application/json' \
  --data '
	{
		"common": {
			"headers": {
				"Authorization": "Bearer supersecrettokenhere"
			}
		},
		"endpoints": [{
            "endpoint": {
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json"
                },
                "url": "http://test-app:8010/results",
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
            }
        },{
            "endpoint": {
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json"
                },
                "url": "http://test-app:8010/results",
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
            }
        }]
}'
```

**Response Example**
```
[
	{
		"id": 236,
		"endpoint": {
			"method": "POST",
			"headers": {
				"Content-Type": "application/json",
				"Authorization": "Bearer supersecrettokenhere"
			},
			"url": "http://test-app:8010/results",
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
		"config": null,
		"batch_id": "caaebb4e90e14cde9473a7e0688794a9",
		"state": "PENDING",
		"state_description": "The test run is queued for processing.",
		"passed": null,
		"test_generated_count": null,
		"test_result_count": null,
		"run_attempts": null,
		"create_date": "2222-01-01T00:00:00",
		"last_update_date": "2222-01-01T00:00:00"
	},
	{
		"id": 240,
		"endpoint": {
			"method": "POST",
			"headers": {
				"Content-Type": "application/json",
				"Authorization": "Bearer supersecrettokenhere"
			},
			"url": "http://test-app:8010/results",
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
		"config": null,
		"batch_id": "caaebb4e90e14cde9473a7e0688794a9",
		"state": "PENDING",
		"state_description": "The test run is queued for processing.",
		"passed": null,
		"test_generated_count": null,
		"test_result_count": null,
		"run_attempts": null,
		"create_date": "2222-01-01T00:00:00",
		"last_update_date": "2222-01-01T00:00:00"
	}
]
```

### Stop a Test Run

Stop a test run that is currently in a state of: PENDING, GENERATING, RUNNING.
After the request, it might take a short amount of time before the test run actually stops.

**Parameters**
**test_run_id: String**

The test run that must be stopped
```
Constraints
- Required
- Maximum length: 50
```

**Request Example**
```
curl --location --request DELETE 'http://localhost/v1/testruns/1'
```

**Response Example**
```
{
	"id": 367,
	"endpoint": {
		"method": "POST",
		"headers": {
			"Content-Type": "application/json"
		},
		"url": "http://test-app:8010/v1/results",
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
	"config": null,
	"batch_id": null,
	"state": "CANCELLED",
	"state_description": "The test run was cancelled.",
	"passed": false,
	"test_generated_count": 259,
	"test_result_count": 259,
	"create_date": "2222-09-18T00:00:00",
	"last_update_date": "2222-09-18T00:00:00"
}
```

### Get all test runs
Get information about all test runs.

**batch_id: String**
The batch id that the test run is a part of. Can be used to quickly get states of all the tests in a batch run.

**state: String**

The state of the test run
```
Constraints
- Allowed values: "PENDING", "GENERATING", "RUNNING", "COMPLETED", "CANCELLED", "FAILED".
```

**passed: Boolean**

Specifies if the test passed the validations that were run against it.
```
Constraints
- Allowed values: "true", "false".
```

**Request Example**

```
curl --location --request GET 'http://localhost/v1/testruns' \
--header 'Accept: application/json'
```

**Response Example**
```
[
    {
		"id": 367,
		"endpoint": {
			"method": "POST",
			"headers": {
				"Content-Type": "application/json"
			},
			"url": "http://test-app:8010/v1/results",
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
		"config": null,
		"batch_id": null,
		"state": "COMPLETED",
		"state_description": "The test run completed successfully.",
		"passed": false,
		"test_generated_count": 259,
		"test_result_count": 259,
		"create_date": "2222-09-18T00:00:00",
		"last_update_date": "2222-09-18T00:00:00"
	}
]
```

### Get Specific Test Run
Get information about a specific test run.

**Parameters**
**test_run_id: String**

The target test run that you need information about.
```
Constraints
- Required
- Maximum length: 50
```

**Request Example**
```
curl --location --request GET 'http://localhost/v1/testruns/1' \
--header 'Accept: application/json'
```

**Response Example**
```
{
	"id": 367,
	"endpoint": {
		"method": "POST",
		"headers": {
			"Content-Type": "application/json"
		},
		"url": "http://test-app:8010/v1/results",
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
	"config": null,
	"batch_id": null,
	"state": "COMPLETED",
	"state_description": "The test run completed successfully.",
	"passed": false,
	"test_generated_count": 259,
	"test_result_count": 259,
	"create_date": "2222-09-18T00:00:00",
	"last_update_date": "2222-09-18T00:00:00"
}
```

## Test Results
### Test Result Object

**test_run_id: String**

The test run that the test was a part of.

**test_type: Enum**

The type of the test that was executed. This can be one of: INTEGER, DOUBLE, STRING, REMOVE.

**test_value: String**

The actual value that was applied to the field in the test, but returned in String form.

**passed: Boolean**

If the test passed all the validations.

**request: Request**

The details of the HTTP request that was performed.

**response: Response**

The details of the HTTP response that was received.

**validations: Array**

The validations that were run against the particular test response.

[See the Analysis Documentation for more information.](./documentation.html#analysis)

Each validation consists of:
- type:
  - The type of validation, such as StatusCode.
- passed:
  - Boolean value indicating wether the validation has passed or not. If this is false for a single validation, the whole test run will not pass.
- message:
  - A description of the outcome such as "Passed", or ax message describing the failure.

**create_date: String**

The date that the result was persisted at.

### Get test results
Get test results for a specific test run.

**Parameters**

**test_run_id: String**

The target test run that you need information about.
```
Constraints
- Maximum length: 50
```

**request_hash: String**

The request_hash (unique identifier) for the test that you need information about.
```
Constraints
- Maximum length: 70
```

**passed: Boolean**

Specifies if the test passed the validations that were run against it.
```
Constraints
- Allowed values: "true", "false".
```

**test_type: String**

The type of the test that was executed.
```
Constraints
- Allowed values: INTEGER, DOUBLE, STRING, REMOVE.
```

**test_value: String**

The actual value that was applied to the field in the test, handled as a String.
```
Constraints
- Maximum length: 10000
```

**method: String**

The http method that will be used.
```
Constraints
- Allowed values: "GET", "POST", "PUT", "DELETE".
```

**request_url: String**

The url that was tested.


**response_status_code: String**

The http response status code that was returned during the test.
```
Constraints
- Mininum value: 0
- Maximum value: 65000
```


**validation_type: String**

The validation that was performed. e.g: `StatusCode`, `Regression`, etc



**Request Example**
```
curl --location --request GET 'http://localhost/v1/testruns/335/tests?passed=0&sort_order=desc' \
--header 'Content-Type: application/json'
```

**Response Example**
```
[
    {
		"test_run_id": "335",
		"test_type": "STRING",
		"test_value": "x",
		"passed": false,
		"request": {
			"hash": "dca8ea32cdde149258ba9a1d885ef5b354df79d4",
			"method": "POST",
			"url": "http://test-app:8010/v1/results",
			"body": {
				"x": [
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
		"response": {
			"hash": "dd70a2c885d60d0d83412946555f5247c21719b9",
			"headers": {
				"Date": "Sat, 17 Sep 2222 00:00:00 GMT",
				"Server": "gunicorn/20.0.4",
				"Connection": "keep-alive",
				"Content-Type": "application/json",
				"Content-Length": "87"
			},
			"body": {
				"id": 0.9459466834709318,
				"test": "value",
				"create_date": "Sat, 17 Sep 2222 00:00:00 GMT"
			},
			"status_code": 200
		},
		"validations": [
			{
				"type": "Status Code",
				"passed": true,
				"message": "Passed",
				"code": "vc_1000"
			},
			{
				"type": "Regression",
				"passed": false,
				"message": "Regression occurred as current response is different from previous response.",
				"code": "vc_3000"
			}
		],
		"create_date": "2222-09-17T00:00:00"
		}
]
```

### Get specific test results
Get a specific test result for a test run.

**Parameters**

**test_run_id: String**

The target test run that you need information about.
```
Constraints
- Required
- Maximum length: 50
```

**test_result_request_hash: String**

The request_hash for the test that you need information about.
```
Constraints
- Required
- Maximum length: 70
```

**Request Example**
```
curl --location --request GET 'http://localhost/v1/testruns/1/tests/dca8ea32cdde149258ba9a1d885ef5b354df79d4' \
--header 'Accept': application/json'
```

**Response Example**
```
{
	"test_run_id": "335",
	"test_type": "STRING",
	"test_value": "x",
	"passed": false,
	"request": {
		"hash": "dca8ea32cdde149258ba9a1d885ef5b354df79d4",
		"method": "POST",
		"url": "http://test-app:8010/v1/results",
		"body": {
			"x": [
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
	"response": {
		"hash": "dd70a2c885d60d0d83412946555f5247c21719b9",
		"headers": {
			"Date": "Sat, 17 Sep 2222 00:00:00 GMT",
			"Server": "gunicorn/20.0.4",
			"Connection": "keep-alive",
			"Content-Type": "application/json",
			"Content-Length": "87"
		},
		"body": {
			"id": 0.9459466834709318,
			"test": "value",
			"create_date": "Sat, 17 Sep 2222 00:00:00 GMT"
		},
		"status_code": 200
	},
	"validations": [
		{
			"type": "Status Code",
			"passed": true,
			"message": "Passed",
			"code": "vc_1000"
		},
		{
			"type": "Regression",
			"passed": false,
			"message": "Regression occurred as current response is different from previous response.",
			"code": "vc_3000"
		}
	],
	"create_date": "2222-09-17T00:00:00"
}
```

### Get test results across all test runs
Get a test results across all test runs. This could be useful to compare results between all test runs.

**Parameters**

**test_run_id: String**

The target test run that you need information about.
```
Constraints
- Maximum length: 50
```

**request_hash: String**

The request_hash (unique identifier) for the test that you need information about.
```
Constraints
- Maximum length: 70
```

**passed: Boolean**

Specifies if the test passed the validations that were run against it.
```
Constraints
- Allowed values: "true", "false".
```

**test_type: String**

The type of the test that was executed.
```
Constraints
- Allowed values: INTEGER, DOUBLE, STRING, REMOVE.
```

**test_value: String**

The actual value that was applied to the field in the test, handled as a String.
```
Constraints
- Maximum length: 10000
```

**method: String**

The http method that will be used.
```
Constraints
- Allowed values: "GET", "POST", "PUT", "DELETE".
```

**request_url: String**

The url that was tested.


**response_status_code: String**

The http response status code that was returned during the test.
```
Constraints
- Mininum value: 0
- Maximum value: 65000
```

**validation_type: String**

The validation type that was returned during the test. Useful for finding tests that contained specific validations.


**Request Example**
```
curl --location --request GET 'http://localhost/v1/tests?passed=0&test_type=STRING&test_value=x&sort_order=desc' \
--header 'Accept': application/json'
```

**Response Example**
```
[
	{
		"test_run_id": "335",
		"test_type": "STRING",
		"test_value": "x",
		"passed": false,
		"request": {
			"hash": "dca8ea32cdde149258ba9a1d885ef5b354df79d4",
			"method": "POST",
			"url": "http://test-app:8010/v1/results",
			"body": {
				"x": [
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
		"response": {
			"hash": "dd70a2c885d60d0d83412946555f5247c21719b9",
			"headers": {
				"Date": "Sat, 17 Sep 2222 00:00:00 GMT",
				"Server": "gunicorn/20.0.4",
				"Connection": "keep-alive",
				"Content-Type": "application/json",
				"Content-Length": "87"
			},
			"body": {
				"id": 0.9459466834709318,
				"test": "value",
				"create_date": "Sat, 17 Sep 2222 00:00:00 GMT"
			},
			"status_code": 200
		},
		"validations": [
			{
				"type": "Status Code",
				"passed": true,
				"message": "Passed",
				"code": "vc_1000"
			},
			{
				"type": "Regression",
				"passed": false,
				"message": "Regression occurred as current response is different from previous response.",
				"code": "vc_3000"
			}
		],
		"create_date": "2222-09-17T00:00:00"
	}
]
```

### Get test run reports
Get reports that can be run to gain deeper insight into test run results.

**Parameters**

**test_run_id: String**

The target test run that you need information about.
```
Constraints
- Required
- Maximum length: 50
```


**Request Example**
```
curl --location --request GET 'http://localhost/v1/testruns/1/reports' \
--header 'Accept': application/json'
```

**Response Example**
```
{
	"reports": [
		"test_results_by_value",
		"test_results_by_status_code",
		"test_result_by_validation"
	]
}
```

### Run a specific test run report
Run a specific test run report.

[See the Report Documentation for more information.](./documentation.html#reporting)

**Parameters**

**test_run_id: String**

The target test run that you need information about.
```
Constraints
- Required
- Maximum length: 50
```

**report_id: String**

The report id that you want to run.
```
Constraints
- Required
```

**Request Example**
```
curl --location --request GET 'http://localhost/v1/testruns/1/reports/test_results_by_status_code' \
--header 'Accept': application/json'
```

**Response Example**
```
[
	{
		"status_code": 404,
		"count": 50
	},
	{
		"status_code": 200,
		"count": 208
	},
	{
		"status_code": 503,
		"count": 1
	}
]
```
