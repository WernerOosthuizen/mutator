Mutator
------
An API fuzzer that exposes RESTful API's to create and monitor fuzzing test runs.

Features
---------------
- Recursive: Mutator will automatically test values deep in nested datastructures (see example tests below).
- Extendable: It's easy to add your own test values in plain text files: `src/mutator/config/test_repository`. Add custom validators to the `src/mutator/result_processor/validations` folder. The validators will get picked up and run automatically on each test.
- Concurrent: Mutator can run multiple test runs at the same time. Each test run can run tests concurrently.
- Track progress: You can view the test run progress via the API.
- Analysis: Results are stored in a database which can be queried via the API.
- Dry run: Adding the environmental flag "DRY_RUN" will log the tests that are generated and not run them. This can be useful to see what will be run before committing to an actual test run against a service.

See more detailed information in the docs directory.

Example usage
--------------

You provide an example request for an API that is correct, and Mutator will mutate each value in turn.
See detailed information under the docs directory.

Example Request to Mutator:
```commandline
curl --request POST \
  --url http://localhost:8000/v1/testruns \
  --header 'Content-Type: application/json' \
  --data '{
    "endpoint": {
        "method": "POST",
        "headers": {
            "Content-Type": "application/json"
        },
        "url": "https://api.testingwebsite.com/v1/testing/this/url",
        "body": {
            "these": 1,
            "are": [1,2,3,4],
            "the": {
                "test": {
                    "fields": ["abc", "xyz"]
                }
            }
        }
    }
}'
```
Test examples for the different test types from a Dry run:

INTEGER: 111
```
{"test_run_id": 139, "test_type": "INTEGER", "test_value": "111", "test_hash": "14bad2d5214f705803a23ca1c2c4d2621b78477f", "method": "POST", "url": "https://api.testingwebsite.com/111/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 139, "test_type": "INTEGER", "test_value": "111", "test_hash": "8e80604241548e01e7a49e6ebed272aed603a405", "method": "POST", "url": "https://api.testingwebsite.com/v1/111/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 139, "test_type": "INTEGER", "test_value": "111", "test_hash": "1c730c316497c79a762285dd2baa9a21fd8e3529", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/111/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 139, "test_type": "INTEGER", "test_value": "111", "test_hash": "b8160b8847e725dd0886c1e5a6fac33360ffbc34", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/111", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 139, "test_type": "INTEGER", "test_value": "111", "test_hash": "2f657ccdec050560e6af926c95dda0d0bcbcf83e", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 111, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 139, "test_type": "INTEGER", "test_value": "111", "test_hash": "250d083b7c490a0d39cf05f2d2ba0f7debea9402", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [111, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 139, "test_type": "INTEGER", "test_value": "111", "test_hash": "4b6bbc76b32b4e24297ec74375264333a32dd866", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 111, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 139, "test_type": "INTEGER", "test_value": "111", "test_hash": "08061a23547f19bce0adc149f4ea4a1e6245f561", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 111, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 139, "test_type": "INTEGER", "test_value": "111", "test_hash": "f2159b5e97d0c84c66c82f3aa5a0b9aff3a4da45", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 111], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 139, "test_type": "INTEGER", "test_value": "111", "test_hash": "4002ce0df0785bdf914495f272995b3572d06df7", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": 111, "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 139, "test_type": "INTEGER", "test_value": "111", "test_hash": "fbee552aeebe8df9a42586668a5b8dce87dd44e5", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": [111, "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 139, "test_type": "INTEGER", "test_value": "111", "test_hash": "9feded60ef97bb3322f7c56c861239edefb10e10", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", 111]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 139, "test_type": "INTEGER", "test_value": "111", "test_hash": "a7a255bdf4a8210bfa585163fc6d946e33301f01", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": 111}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 139, "test_type": "INTEGER", "test_value": "111", "test_hash": "ce0fe06d0a31bc9734a5f18f0f49e4c0df03af46", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": 111}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 139, "test_type": "INTEGER", "test_value": "111", "test_hash": "f1c5741a65eec2bb5ceebcbbd46c7833d670ad98", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": 111}, "headers": {"Content-Type": "application/json"}}
```

DOUBLE: 11111.111111
```
{"test_run_id": 154, "test_type": "DOUBLE", "test_value": "11111.111111", "test_hash": "f8c904c80ce49d660bbc13b32569c23c4c01e492", "method": "POST", "url": "https://api.testingwebsite.com/11111.111111/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 154, "test_type": "DOUBLE", "test_value": "11111.111111", "test_hash": "134907e5c603a867b12a1163145d6fbc9227e2d7", "method": "POST", "url": "https://api.testingwebsite.com/v1/11111.111111/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 154, "test_type": "DOUBLE", "test_value": "11111.111111", "test_hash": "c5d42677248908bf8e0b8d4aef8ac5a18b4b0a65", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/11111.111111/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 154, "test_type": "DOUBLE", "test_value": "11111.111111", "test_hash": "2d5541d128cbf64bb6b534f25b28c286e4a8038a", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/11111.111111", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 154, "test_type": "DOUBLE", "test_value": "11111.111111", "test_hash": "bcb932fcc30fa1214307daf3873933add91a42f0", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 11111.111111, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 154, "test_type": "DOUBLE", "test_value": "11111.111111", "test_hash": "ecf363593358011795cb7237c1f620a6516555da", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [11111.111111, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 154, "test_type": "DOUBLE", "test_value": "11111.111111", "test_hash": "d8e30fafc9ff103bbf39b4ae97cf6841fbd231bd", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 11111.111111, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 154, "test_type": "DOUBLE", "test_value": "11111.111111", "test_hash": "2b6fb46992ebaa90663c504ace2b4760e3499e9c", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 11111.111111, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 154, "test_type": "DOUBLE", "test_value": "11111.111111", "test_hash": "915098d5a3ab2aa1df30946f9d68069750d03252", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 11111.111111], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 154, "test_type": "DOUBLE", "test_value": "11111.111111", "test_hash": "50d983f6b0c26ab3ed116d6aea35d9b4e0a88732", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": 11111.111111, "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 154, "test_type": "DOUBLE", "test_value": "11111.111111", "test_hash": "d7da2d6ea49e090543a7d36c39eb1ed2c2cd1d81", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": [11111.111111, "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 154, "test_type": "DOUBLE", "test_value": "11111.111111", "test_hash": "52f5ac08d8d4657a9a0a827ed010d1d0b1d1edb1", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", 11111.111111]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 154, "test_type": "DOUBLE", "test_value": "11111.111111", "test_hash": "5963276635a9511270b23ce2ecb1ec014dc22f26", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": 11111.111111}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 154, "test_type": "DOUBLE", "test_value": "11111.111111", "test_hash": "7af4876720d31ee3af0b58be572e03947a4b9d5a", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": 11111.111111}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 154, "test_type": "DOUBLE", "test_value": "11111.111111", "test_hash": "895c3284ed3d7a12b20ee4241084703e580f5dd5", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": 11111.111111}, "headers": {"Content-Type": "application/json"}}

```

STRING: xxxxx
```
{"test_run_id": 140, "test_type": "STRING", "test_value": "xxxxx", "test_hash": "1098410c2ac0577b8c8009fb09eaf573c65980cf", "method": "POST", "url": "https://api.testingwebsite.com/xxxxx/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 140, "test_type": "STRING", "test_value": "xxxxx", "test_hash": "fefabdb95e982924e64b14dd9d6cd41ad9724862", "method": "POST", "url": "https://api.testingwebsite.com/v1/xxxxx/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 140, "test_type": "STRING", "test_value": "xxxxx", "test_hash": "d6e462df80f88a6d193f953dd9dea60f62180be7", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/xxxxx/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 140, "test_type": "STRING", "test_value": "xxxxx", "test_hash": "7c72e7d6552ea8185b3dd5ab1d4bb40e21261631", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/xxxxx", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 140, "test_type": "STRING", "test_value": "xxxxx", "test_hash": "d36e6351dfe0115c34fd7822719c76518059e9ed", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"xxxxx": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 140, "test_type": "STRING", "test_value": "xxxxx", "test_hash": "e7f24e7654c0e571a418a72d148808c1a158a39a", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": "xxxxx", "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 140, "test_type": "STRING", "test_value": "xxxxx", "test_hash": "a3571fc7264dca51c99017240c7b6168f59aabe3", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": ["xxxxx", 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 140, "test_type": "STRING", "test_value": "xxxxx", "test_hash": "6344d57607319ed4d52cdcd32c91b82f742ba439", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, "xxxxx", 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 140, "test_type": "STRING", "test_value": "xxxxx", "test_hash": "18d3424fc70c666d17dac79790fd062e6b36e108", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, "xxxxx", 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 140, "test_type": "STRING", "test_value": "xxxxx", "test_hash": "daffbd5d8e3e7c8d9df38d7c2db4ea72b035cfa8", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, "xxxxx"], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 140, "test_type": "STRING", "test_value": "xxxxx", "test_hash": "21170d85c8b5ad5158859e82a85b19e4f72a7e7b", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "xxxxx": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 140, "test_type": "STRING", "test_value": "xxxxx", "test_hash": "3d21e7acfcc779ab554e5e3c91db6be8686395ae", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": "xxxxx", "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 140, "test_type": "STRING", "test_value": "xxxxx", "test_hash": "3d41550d2215e1a0678faa3a9ba04a09432e7356", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["xxxxx", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 140, "test_type": "STRING", "test_value": "xxxxx", "test_hash": "94ce55554706794d77c434b6a7bb6af39c2d3712", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xxxxx"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 140, "test_type": "STRING", "test_value": "xxxxx", "test_hash": "5e929a0814a48f02de0a3dcac1039a24bb0bf1ac", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"xxxxx": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 140, "test_type": "STRING", "test_value": "xxxxx", "test_hash": "626a3c01520a6a29801454ca0cff482647263853", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": "xxxxx"}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 140, "test_type": "STRING", "test_value": "xxxxx", "test_hash": "3d9916f1ed6e783f45b8470a9f2a655d36836ca6", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"xxxxx": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 140, "test_type": "STRING", "test_value": "xxxxx", "test_hash": "3d7beb348e0f4f0e44172ae1db2647494b47d624", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": "xxxxx"}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 140, "test_type": "STRING", "test_value": "xxxxx", "test_hash": "deb7a331a7d51c3aa05f52c81faca5e991ca2437", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "xxxxx": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 140, "test_type": "STRING", "test_value": "xxxxx", "test_hash": "2ddefd2d29f30e505239787e5cfb23456baf8684", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": "xxxxx"}, "headers": {"Content-Type": "application/json"}}
```

REMOVE: This removes each value once per test
```
{"test_run_id": 141, "test_type": "REMOVE", "test_value": "remove_field", "test_hash": "67e72abb8dd6d0236c4a36340ca61a43c3e8041a", "method": "POST", "url": "https://api.testingwebsite.com/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 141, "test_type": "REMOVE", "test_value": "remove_field", "test_hash": "ef499528e7ca903c3f331bf1c7acab80bdd11c42", "method": "POST", "url": "https://api.testingwebsite.com/v1/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 141, "test_type": "REMOVE", "test_value": "remove_field", "test_hash": "96453044ef4bd1d9b3a302247e231057d74ab6be", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 141, "test_type": "REMOVE", "test_value": "remove_field", "test_hash": "54776ed93022ca1b29dbd8243102fc18d8c5c5b4", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 141, "test_type": "REMOVE", "test_value": "remove_field", "test_hash": "3632058dec13be34485c21edbcad382331a44191", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 141, "test_type": "REMOVE", "test_value": "remove_field", "test_hash": "cb6c62490f6e078ff64affb1ae708fac22f5e047", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [2, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 141, "test_type": "REMOVE", "test_value": "remove_field", "test_hash": "733d0139f12b23231200335bd2232117ccf418e3", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 3, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 141, "test_type": "REMOVE", "test_value": "remove_field", "test_hash": "8775e726b65de9fbae2403a9c03a0277bccbd101", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 4], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 141, "test_type": "REMOVE", "test_value": "remove_field", "test_hash": "b5edee2ffdf5dc265fe1ce1cc3e2cbd02f1e94ea", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3], "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 141, "test_type": "REMOVE", "test_value": "remove_field", "test_hash": "64a9758b0004562a5e2980d3d03cc757e432316c", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "the": {"test": {"fields": ["abc", "xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 141, "test_type": "REMOVE", "test_value": "remove_field", "test_hash": "f6034ff286cdf73b644da23dc38fcf49e51835f8", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["xyz"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 141, "test_type": "REMOVE", "test_value": "remove_field", "test_hash": "a0703d726bdddf405d546dac1819ccb317c089f0", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {"fields": ["abc"]}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 141, "test_type": "REMOVE", "test_value": "remove_field", "test_hash": "cafd192e92fa4d3084f4ff199b15f3ad03454519", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {"test": {}}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 141, "test_type": "REMOVE", "test_value": "remove_field", "test_hash": "c98869ea462be361e1ff1ca448486a26d1c48094", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4], "the": {}}, "headers": {"Content-Type": "application/json"}}
{"test_run_id": 141, "test_type": "REMOVE", "test_value": "remove_field", "test_hash": "80006948a25d7ebc99065b1b2a3935cf65240358", "method": "POST", "url": "https://api.testingwebsite.com/v1/testing/this/url", "body": {"these": 1, "are": [1, 2, 3, 4]}, "headers": {"Content-Type": "application/json"}}
```

The test values that are used (and can easily be updated) live at `src/mutator/config/test_repository`.

Getting Started
---------------

Build:
```
docker build . -t mutator
```

Run:

Mounting the `database` folder when using sqlite is optional:
```
docker run \
-d \
-p 80:8000 \
-v /home/user/Documents/data_dir_here/database:/app/data/database \
mutator
```

Alternatively, a docker-compose.yml file is supplied that can be used.
If you don't wish to use docker, the `startup.sh` script in the project root can be used.

Create test run targeting `www.test-app.com` with a POST request:
```
curl --request POST \
  --url http://localhost:80/v1/testruns \
  --header 'Content-Type: application/json' \
  --data '{
    "endpoint": {
        "method": "POST",
        "headers": {
            "Content-Type": "application/json"
        },
        "url": "https://www.test-app.com/super/cool/endpoint",
        "body": {
            "lets": [1,2,3],
            "break": {
                "something": "yay"
            }
        }
    }
}
'

```
GET test run status
```
curl --request GET --url 'http://localhost:80/v1/testruns?sort_order=desc'
```

GET test results specific to a test run
```
curl --request GET --url 'http://localhost:80/v1/testruns/1/tests?sort_order=desc'
```

GET all test results
```
curl --request GET --url 'http://localhost:80/v1/tests?sort_order=desc'

```

The tests can currently be filtered by the following query params:
- test_run_id
- request_hash
- passed
- test_type
- test_value
- method
- request_url
- response_status_code
- validation_type

See the docs directory for more information.
