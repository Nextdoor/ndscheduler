/**
 * jobs-table view.
 *
 * @author wenbin@nextdoor.com
 */

require.config({
  paths: {
    'jquery': 'vendor/jquery',
    'underscore': 'vendor/underscore',
    'backbone': 'vendor/backbone',
    'bootstrap': 'vendor/bootstrap',
    'datatables': 'vendor/jquery.dataTables',

    'utils': 'utils',
    'run-job-view': 'views/jobs/run-job-view',
    'edit-job-view': 'views/jobs/edit-job-view',

    'text': 'vendor/text',
    'job-row-name': 'templates/job-row-name.html',
    'job-row-action': 'templates/job-row-action.html'
  },

  shim: {
    'bootstrap': {
      deps: ['jquery']
    },

    'backbone': {
      deps: ['underscore', 'jquery'],
      exports: 'Backbone'
    },

    'datatables': {
      deps: ['jquery'],
      exports: '$.fn.dataTable'
    }
  }
});

define(['utils',
        'run-job-view',
        'edit-job-view',
        'text!job-row-name',
        'text!job-row-action',
        'backbone',
        'bootstrap',
        'datatables'], function(utils,
                                RunJobView,
                                EditJobView,
                                JobRowNameHtml,
                                JobRowActionHtml) {
  'use strict';

  return Backbone.View.extend({

    initialize: function() {
      this.listenTo(this.collection, 'sync', this.render);
      this.listenTo(this.collection, 'request', this.requestRender);
      this.listenTo(this.collection, 'reset', this.resetRender);
      this.listenTo(this.collection, 'error', this.requestError);

      $('#jobs-refresh-button').on('click', _.bind(this.resetRender, this));
      $('#display-tz').on('change', _.bind(this.resetRender, this));

      // Initialize data table
      this.table = $('#jobs-table').dataTable({
        // Sorted by job name
        'order': [[0, 'asc']]
      });
    },

    /**
     * Request error handler.
     *
     * @param {object} model
     * @param {object} response
     * @param {object} options
     */
    requestError: function(model, response, options) {
      this.spinner.stop();
      utils.alertError('Request failed: ' + response.responseText);
    },

    /**
     * Event handler for starting to make network request.
     */
    requestRender: function() {
      this.table.fnClearTable();
      this.spinner = utils.startSpinner('jobs-spinner');
    },

    /**
     * Event handler for resetting jobs data.
     *
     * This is registered with click handlers for the #jobs-refresh-button, the #display-tz
     * dropdown, as well as this collection.  When called from the collection, no parameter
     * is given.
     */
    resetRender: function(e) {
      // It'll trigger sync event
      if (e) {
        e.preventDefault();
      }
      this.collection.getJobs();
    },

    /**
     * Event handler for finishing fetching jobs data.
     */
    render: function() {
      var jobs = this.collection.jobs;

      var data = [];

// Build up data to pass to data tables
				_.each(jobs, function(job) {
					var jobObj = job.toJSON();

          var jobRowNameArguments = {
            'job_name': _.escape(jobObj.name),
            'job_schedule': job.getScheduleString(),
            'next_run_at': job.getNextRunTimeHTMLString(),
            'job_id': jobObj.job_id,
            'job_class': _.escape(jobObj.job_class_string),
            'job_active': job.getActiveString(),
            'job_pubargs': _.escape(job.getPubArgsString()),
            'job_trigger': _.escape(jobObj.trigger),
            'job_trigger_params': _.escape(JSON.stringify(jobObj.trigger_params)),
          }

					data.push([
							_.template(JobRowNameHtml)(jobRowNameArguments),
							job.getScheduleString(),
							job.getNextRunTimeHTMLString(),
							_.template(JobRowActionHtml)({
								'job_name': _.escape(jobObj.name),
								'job_id': jobObj.job_id,
								'job_class': _.escape(jobObj.job_class_string),
								'job_pubargs': _.escape(job.getPubArgsString())
							})
						]);
				});

      if (data.length) {
        this.table.fnClearTable();
        this.table.fnAddData(data);
      }

      // Stop the spinner
      this.spinner.stop();

      // Set up the RunJob thing
      new RunJobView({
        collection: this.collection
      });

      // Set up EditJob thing
      new EditJobView({
        collection: this.collection
      });

    }
  });
});
