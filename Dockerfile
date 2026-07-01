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

#FROM  python:3.8.3-alpine
FROM nikolaik/python-nodejs:python3.11-nodejs20

# Run root-level installs and prepare app directory
RUN pip3 install --upgrade pip && \
    npm install -g fsh-sushi@3.11.1 && \
    mkdir -p /app && chown pn:pn /app

# Switch to non-root user; HOME=/home/pn, so pip --user and sushi cache
# both live under /home/pn and are accessible at runtime
USER pn
WORKDIR /app

COPY --chown=pn:pn requirements.txt requirements.txt
RUN pip3 install --user -r requirements.txt

COPY --chown=pn:pn . .

#CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

CMD ["python3", "app.py"]

#EXPOSE 5000