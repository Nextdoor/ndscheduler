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
		'job-row-name-cron'     : 'templates/job-row-name-cron.html',
		'job-row-name-interval' : 'templates/job-row-name-interval.html',
		'job-row-name-unknown'  : 'templates/job-row-name-unknown.html',
		'job-row-actions'        : 'templates/job-row-actions.html'
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
		'text!job-row-name-cron',
		'text!job-row-name-interval',
		'text!job-row-name-unknown',
		'text!job-row-actions',
		'backbone',
		'bootstrap',
		'datatables'],
	function(utils,
			RunJobView,
			EditJobView,
			JobRowNameHtmlCron,
			JobRowNameHtmlInterval,
			JobRowNameHtmlUnknown,
			JobRowActionsHtml
			)
	{
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
					'order': [[0, 'asc']],
					"iDisplayLength": 50
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

					console.log("Job:")
					console.log(jobObj)

					if (jobObj.trigger_type == 'cron')
					{
						data.push([
							_.template(JobRowNameHtmlCron)({
								'job_name': _.escape(jobObj.name),
								'job_schedule': job.getScheduleString(),
								'next_run_at': job.getNextRunTimeHTMLString(),
								'job_id': jobObj.job_id,
								'job_class': _.escape(jobObj.job_class_string),
								'job_sched_type': _.escape("Cron"),
								'job_month': _.escape(jobObj.month),
								'job_day_of_week': _.escape(jobObj.day_of_week),
								'job_day': _.escape(jobObj.day),
								'job_hour': _.escape(jobObj.hour),
								'job_minute': _.escape(jobObj.minute),
								'job_active': job.getActiveString(),
								'job_pubargs': _.escape(job.getPubArgsString())
							}),
							job.getScheduleString(),
							job.getNextRunTimeHTMLString(),
							_.template(JobRowActionsHtml)({
								'job_name': _.escape(jobObj.name),
								'job_id': jobObj.job_id,
								'job_class': _.escape(jobObj.job_class_string),
								'job_pubargs': _.escape(job.getPubArgsString())
							})
						]);
					}


					else if (jobObj.trigger_type == 'interval')
					{
						data.push([
							_.template(JobRowNameHtmlInterval)({
								'job_name': _.escape(jobObj.name),
								'job_schedule': job.getScheduleString(),
								'next_run_at': job.getNextRunTimeHTMLString(),
								'job_id': jobObj.job_id,
								'job_class': _.escape(jobObj.job_class_string),
								'job_sched_type': _.escape("Interval"),
								'job_interval': _.escape(jobObj.interval),
								'job_active': job.getActiveString(),
								'job_pubargs': _.escape(job.getPubArgsString())
							}),
							job.getScheduleString(),
							job.getNextRunTimeHTMLString(),
							_.template(JobRowActionsHtml)({
								'job_name': _.escape(jobObj.name),
								'job_id': jobObj.job_id,
								'job_class': _.escape(jobObj.job_class_string),
								'job_pubargs': _.escape(job.getPubArgsString())
							})
						]);
					}
					else
					{
						data.push([
							_.template(JobRowNameHtmlUnknown)({
								'job_name': _.escape(jobObj.name),
								'job_schedule': job.getScheduleString(),
								'next_run_at': job.getNextRunTimeHTMLString(),
								'job_id': jobObj.job_id,
								'job_class': _.escape(jobObj.job_class_string),
								'job_sched_type': _.escape("Unknown"),
								'job_active': job.getActiveString(),
								'job_pubargs': _.escape(job.getPubArgsString())
							}),
							job.getScheduleString(),
							job.getNextRunTimeHTMLString(),
							_.template(JobRowActionsHtml)({
								'job_name': _.escape(jobObj.name),
								'job_id': jobObj.job_id,
								'job_class': _.escape(jobObj.job_class_string),
								'job_pubargs': _.escape(job.getPubArgsString())
							})
						]);
					}



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
	}
);
