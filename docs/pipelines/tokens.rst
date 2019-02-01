.. _pipelinejobs-tokens:

====================
Authorization Tokens
====================

Every PipelineJob is secured with one or more tokens that must be passed with
every event or management request that could result in a change in state or
availability of a job.

There are two kinds of tokens: Job-scoped tokens are cryptographically
distinct and can authorize most events for one specific PipelineJob. The
exceptions are the ``reset``, ``ready``, and ``delete`` events, which can only
be authorized by Administrative tokens.

Job-scoped Tokens
-----------------

Below is an example of capturing and re-using a job-scoped token while
managing a PipelineJob.

.. code-block:: pycon

   ...
   >>> mpj = ManagedPipelineJob(mongodb, pipelines, agave=agave_client, ...)
   >>> mpj.setup()
   >>> resp = mpj.run()
   >>> token = resp.get('token')
   >>> jid = resp.get('uuid')
   >>> print(token, jid)
   a3b29f2c62ec9d15 1071269f-b251-5a5f-bec1-6d7f77131f3f

Now, assume some magic happens and there is another process that needs to
manage the job we just set up. Assume also that you remembered the job UUID and
token and have passed it into the process. The example below illustrates
initializing a ```ManagedPipelineJobInstance``` and using it to trigger an
**update**b event.

.. code-block:: pycon

   >>> from datacatalog.managers.pipelinejobs import ManagedPipelineJobInstance
   >>> job_uuid='1071269f-b251-5a5f-bec1-6d7f77131f3f'
   >>> job_token='a3b29f2c62ec9d15'
   >>> mongodb={'authn': 'bW9uZ29kYjov...jRWJTI2SCUyQiy1zdGFnIwL2W1hcnk='}
   >>> mpji = ManagedPipelineJobInstance(mongodb, job_uuid, token=job_token)
   >>> resp = mpji.update()
   >>> token = resp.get('token')
   >>> print(token)
   a3b29f2c62ec9d15

Administrative Tokens
---------------------

These powerful credentials authorize **any** event for **any** PipelineJob,
including ``reset``, ``ready``, and ``delete``. To limit the risks of such
power being included in a git commit or send over email, administrative tokens
are invalidated and reset every {{opt_admin_token_lifetime}} seconds. To
generate and receice an administrative token, you must supply a valid
**Admin Token Key**, which is provided on request after a review of your
planned use case and your readiness to use it safely.

Retrieve and Validate a Token
#############################

.. code-block:: pycon

   >>> from datacatalog.tokens import get_admin_token, validate_token
   >>> from datacatalog.tokens import get_admin_lifetime
   >>> from time import sleep
   >>> akey = 'STbmczGuxqvQSN6YCaA2CmHbpet2tZHc'
   >>> atoken = get_admin_token(akey)
   >>> validate_token(atoken)
   True
   >>> sleep(get_admin_lifetime * 2)
   >>> validate_token(atoken)
   False
   >>> atoken = get_admin_token(akey)
   >>> validate_token(atoken)
   True

This token can be used in lieu of a Job-scoped token. The example below
illustrates using it for an **update** event, then for a **reset** event,
which is priviledged action.

Use the Administrative Token
#############################

.. code-block:: pycon

   >>> from datacatalog.managers.pipelinejobs import ManagedPipelineJobInstance
   >>> from datacatalog.tokens import get_admin_token
   >>> mongodb={'authn': 'bW9uZ29kYjov...jRWJTI2SCUyQiy1zdGFnIwL2W1hcnk='}
   >>> akey = 'STbmczGuxqvQSN6YCaA2CmHbpet2tZHc'
   >>> atoken = get_admin_token(akey)
   >>> mpji = ManagedPipelineJobInstance(mongodb, job_uuid, token=atoken, ...)
   >>> update_doc = {'uuid': self.uuid,
                     'name': 'reset;,
                     'data': {}}
   >>> mpji.handle(update_doc, atoken)
   >>> reset_doc = {'uuid': self.uuid,
                    'name': 'reset;,
                    'data': {}}
   >>> mpji.handle(reset_doc, atoken)
