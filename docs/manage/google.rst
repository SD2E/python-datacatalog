=========================
Syncing with Google Drive
=========================

The **challenges** and **experiment_designs** schemas and MongoDB collections
are built (at present) by querying the **CP Working Groups** directory on the
project Google Drive. Directory names are resolved into Challenge Problem
records. The experiment request documents in each directory are resolved into
Experiment Design records. Creation and update dates for each record are
maintained to give some sense of the timeline of various experiment
requests. A URL-safe unique identifier is created from the title of each
CP or Experiment Request and used to define the enumerated schema of
challenge problem and experiment design identifiers:

* `challenge problem <https://schema.catalog.sd2e.org/schemas/challenge_problem_id.json>`
* `experiment design <https://schema.catalog.sd2e.org/schemas/experiment_reference.json>`

Updating
--------

.. code-block:: console

   # Update locally first
   python -m scripts.build_challenge_problems -localhost
   python -m scripts.build_experiment_designs -localhost
   # Regenerate schemas
   git checkout develop
   git pull origin develop
   python -m scripts.build_schemas -localhost
   # Add schemas to git
   git add datacatalog/definitions/jsondocs/challenge_problem_id.json
   git add datacatalog/definitions/jsondocs/experiment_reference.json
   git add schemas
   git commit -m "Regenerated CP/EXD schemas from Google Drive"
   git checkout gh-pages
   git merge develop
   git push origin gh-pages
   git checkout develop
   # Update production (or staging or development)
   python -m scripts.build_challenge_problems -production
   python -m scripts.build_experiment_designs -production

