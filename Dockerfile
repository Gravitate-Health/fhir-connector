# Copyright 2022 Universidad Politécnica de Madrid 
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM  python:3.8.3-alpine

RUN pip3 install --upgrade pip

# Set to a non-root built-in user `fhir`
RUN adduser -D myuser 
USER myuser
WORKDIR /home/myuser

COPY --chown=myuser:myuser requirements.txt requirements.txt
RUN pip3 install --user -r requirements.txt

COPY --chown=myuser:myuser . .

ENV PATH="/home/myuser/.local/bin:${PATH}"

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

EXPOSE 5000