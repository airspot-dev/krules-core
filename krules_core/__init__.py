# Copyright 2019 The KRules Authors
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class TopicsDefault:

    RESULTS = "RulesResults"
    #RESULTS_FULL = "RulesResultsFull"
    ERRORS = "RulesErrors"


class RuleConst(object):
    """
    Basic consts
    """

    PROCESS_ID = "process_id"
    ORIGIN_ID = "origin_id"
    RULENAME = "rulename" # TODO.. rule_name/rulename
    DESCRIPTION = "description"
    SUBSCRIBE_TO = "subscribe_to"
    RULEDATA = "ruledata"

    FILTERS = "filters"
    PROCESSING = "processing"
    FINALLY = "finally"

    MESSAGE = "message"
    SUBJECT = "subject"
    RULE_NAME = "rule_name"
    SECTION = "section"
    FUNC_NAME = "func_name"
    PAYLOAD = "payload"
    ARGS = "args"
    KWARGS = "kwargs"
    RETURNS = "returns"
    PROCESSED = "processed"
    EVENT_INFO = "event_info"

    GOT_ERRORS = "got_errors"
    EXCEPTION = "exception"
    EXC_INFO = "exc_info"
    EXC_EXTRA_INFO = "exc_extra_info"

class ConfigKeyConst(object):

    MESSAGE_TOPICS_PREFIX = "MESSAGE_TOPICS_PREFIX"
