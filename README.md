# Skurge 
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE.txt) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](resources/contributing.md)
<br />[![](https://img.shields.io/badge/code--coverage-95%25-brightgreen)](coverage.xml)
<br />![](https://img.shields.io/badge/Python-3.9-green) ![](https://img.shields.io/badge/Django-2.2-green) ![](https://img.shields.io/badge/PostgreSQL-12-blue)

Skurge is a generic and configuration driven data transformation and data relay service, implementing an if-this-then-that architecture.

Microservice based business software have many underlying services interacting with each other and constantly generating data. 
Transforming this data and relaying it to appropriate systems is a common and necessary requirement.
For example, sending your data to an analytics service for business insights or sending it to a communication service to send emails to the customer
or establishing asynchronous communication links among your services and much more.

Handling all these requirements individually in different services may lead to code repetition, bloat, frequent code changes and overloading core business services with auxiliary work.

With this, comes a need of a service that can reliably handle performing DTS actions on a particular trigger based on stored configurations, and further relay the transformed data to other services, via different protocols.


### Solution: Skurge!
Skurge is a ready-to-use generic and low maintenance service, configuration driven solution to the above problem.

It receives data, validates it against the schema you define, aggregates more data associated endpoints via a GraphQL layer, and relays it to appropriate systems via two currently supported protocols: HTTP, and AMQP. It supports conditional logic throughout the flow. 

Skurge offers following benefits:
* It is completely database configuration driven. No code changes are required for registering a new data processing and relaying flow in skurge. You just need to make entries in skurge's database tables. 
* It can be easily integrated as a microservice in your software.
* It works asynchronously. You can trigger it with necessary input payload and leave the rest for skurge to handle.
* It logs relay status in database table which can be used for quick and convenient debugging.

---
## Table of Contents
* [Installation](#Installation)
  * [Dependencies](#Dependencies)
  * [Setting up](#Setting-up)
  * [Configuration](#Configuration)
  * [Running](#Running)
  * [Testing](#Testing)
* [Architecture](#Architecture)
* [APIs](#APIs)
* [Contributing](#Contributing)
  * [Code of Conduct](#Code-of-Conduct)
  * [Contributing Guide](#Contributing-Guide)
* [License](#License)
* [How we use Skurge at Livspace](#How-we-use-Skurge-at-Livspace)
* [Contact](#Contact)
---

## Installation


### Dependencies
* `Python 3.9`
* The service is written in `Django` & uses `PostrgeSQL` as database.
* [GraphQL](https://graphql.org/), [JsonLogic](https://jsonlogic.com/), [JsonSchema](https://json-schema.org/) and [Pydash](https://pydash.readthedocs.io/en/latest/) libraries.
* Package dependencies are mentioned in [requirements.txt](requirements.txt)

### Setting up
* Fork and/or clone the repository
* Create and activate a python virtual environment
* Install dependencies in [requirements.txt](requirements.txt) by running `pip install -r requirements.txt`

### Configuration
* Update configurations in [configuration file](webapp/conf/env/conf.py).
* You may also want to review settings in [settings file](webapp/conf/settings.py) and [docker file](Dockerfile).

### Running
* Database migration files are present in [migrations](webapp/apps/skurge/migrations) folder. Run db migration by running `python manage.py migrate`
* The service is a django application and can be run by `python manage.py runserver`. The default port is `7042` which may be updated in [manage.py](manage.py) file.
* You may change [Dockerfile](Dockerfile) to build and deploy docker image.

### Testing
* Integration tests are present in [tests folder](webapp/apps/skurge/tests). You can run the tests by running `python manage.py test`
* Test coverage: > 95%
* The service uses [django-nose](https://pypi.org/project/django-nose/) for testing and code coverage. The configurations for the same are defined in [settings file](webapp/conf/settings.py).
* Sample test data can be found in [constants file](webapp/apps/skurge/tests/common/constants.py). The sample data simulates following scenario:
  * Skurge receives `TEST_EVENT` with `user_id` as input payload.
  * Skurge fetches `name`,`email` and `country code` from the graphql server for the `user_id`.
  * Depending upon country being that of India (`IN`) or not, it prepares two different payloads having user `name` and email `template id`.
  * `from` (eg. your company's email) and `to` (customer email) are also added to final payload as defaults.
  * The final payload is validated against json schema.
  * An event `SEND_EMAIL` is published to messaging queue with final payload prepared above. The payload is meant for system `notification-service`. This may be your notification service which can then send email to the customer.
  * Alternatively, one can also hit an API of an `external-service` depending on user's `country code`.

## Architecture
Checkout [the architecture of Skurge](resources/architecture.md) to learn about data flow and database schema.

## APIs
Please use the [OpenAPI specs](resources/apis.md) for development using its APIs.


## Contributing

### Code of Conduct
Livspace has adopted a Code of Conduct that we expect project participants to adhere to. Read our [code of conduct](resources/code_of_conduct.md).

### Contributing Guide
The main purpose of this repository is to continue evolving Skurge. We are grateful to the community for contributing bugfixes and improvements.

Read our [contribution guidelines](resources/contributing.md) to learn about how to propose bugfixes and improvements.

## License
This project is licensed under the terms of Apache license, Version 2.0 ([LICENSE](LICENSE.txt))

## How we use Skurge at Livspace
At [Livspace](https://www.livspace.com/), we use Skurge across teams for various async transformation + relay activities. We will focus here on one such critical aspect: customer communication. In conjunction with our notification service, we use Skurge to manage all our customer communications by relaying data to our customer relationship management partners. We also use skurge to send appropriate payload to our analytics services, based on various AMQP events that happen within the ecosystem. 

```mermaid
sequenceDiagram
  Service A ->> AMQP: Emits an event with necessary payload
  Skurge ->> AMQP: Reads from the queue and parses the payload
  Skurge ->> Database: Fetches the configuration for the particular event type
  Skurge ->> GraphQL: Requests for all needed data using GQL queries as per configuration
  GraphQL ->> Skurge:  All requested data fields
  Skurge ->> Skurge: Transforms data according to the data transformer logic
  Skurge ->> Other Services: Relays data to services
 ```

Key highlights of our journey, so far:
* We migrated our old, code-driven customer communications to skurge in less than 3 months. It is now a single point of reference to manage our 60+ touchpoints of critical customer communications. 
* Skurge is designed to be developer friendly, bugs free and low maintenance service. We built it in mid of 2021 and haven't faced any issues ever since. The logs table and verbose logging has helped our developers save time and efforts. 
* The learning curve to add new skurge configurations is short. One need not be a developer to learn the syntax. The average learning time to fully understand the service has been less than 3 days.
* New configurations can be prepared in a matter of hours. Any new data transformation & relay flow can be prepared, tested and moved to production in a day. The average is 2 days for us, the best being under 15 minutes.
* We have deprecated some of our microservices and moved them fully as configurations in skurge. This has helped us cut down our technology infrastructure costs.


## Contact
You may contact the developers:
* [Vinamra Arya](https://github.com/vinamraarya-livspace) (vinamra.arya@livspace.com)
* [Onkar Hoysala](https://github.com/onkarhoysalalivspace) (onkar.hoysala@livspace.com)
* [Ayur Jain](https://github.com/aj95) (ayur.jain@livspace.com)

You can contact the organisation: [Livspace](https://www.livspace.com/in/contact-us)
