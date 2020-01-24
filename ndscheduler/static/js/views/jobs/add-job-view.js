/**
 * add-job view.
 *
 * @author wenbin@nextdoor.com
 */

require.config({
  paths: {
    'jquery': 'vendor/jquery',
    'underscore': 'vendor/underscore',
    'backbone': 'vendor/backbone',
    'bootstrap': 'vendor/bootstrap',
    'select2': 'vendor/select2',

    'utils': 'utils',

    'text': 'vendor/text',
    'add-job-modal': 'templates/add-job.html',
    'job-class-notes': 'templates/job-class-notes.html'
  },

  shim: {
    'bootstrap': {
      deps: ['jquery']
    },

    'select2': {
      deps: ['jquery']
    },

    'backbone': {
      deps: ['underscore', 'jquery'],
      exports: 'Backbone'
    }
  }
});

define(['utils',
  'text!add-job-modal',
  'text!job-class-notes',
  'backbone',
  'bootstrap',
  'select2'], function(utils, AddJobModalHtml, JobClassNotesHtml) {

  'use strict';

  return Backbone.View.extend({
    initialize: function() {

      $('body').append(AddJobModalHtml);

      $('#input-job-trigger').val("cron");

      this.bindAddJobConfirmClickEvent();
      this.bindJobTriggerTabChangedEvent();

      var jobsMetaInfo = $.parseJSON($('#jobs-meta-info').html());
      var data = [];
      _.forEach(jobsMetaInfo, function(job) {
        data.push({
          id: job.job_class_string,
          text: job.job_class_string,
          job: job
        })
      });
      $('#input-job-task-class').select2({
        placeholder: "Select an job class, please",
        data: data
      }).on("select2-selecting", function(e) {
        $('#add-job-class-notes').html(
            _.template(JobClassNotesHtml)({job: e.choice.job})
        );
      });

    },

    bindJobTriggerTabChangedEvent: function() {
      $('#input-trigger-tab a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        //show selected tab / active
        var trigger = $(e.target).attr('id');
        $('#input-job-trigger').val(trigger);
      });

    },

    bindAddJobConfirmClickEvent: function() {

      $('#add-job-confirm-button').on('click', _.bind(function(e) {
        e.preventDefault();

        var jobName = $('#input-job-name').val();
        var jobTask = $('#input-job-task-class').val();
        var trigger = $('#input-job-trigger').val().toLowerCase();
        var args = $('#input-job-task-args').val();


        var trigger_params = {};

        if(trigger.toLowerCase() == "cron"){
          trigger_params.month = $('#input-job-month').val();
          trigger_params.day_of_week = $('#input-job-day-of-week').val();
          trigger_params.day = $('#input-job-day').val();
          trigger_params.hour = $('#input-job-hour').val();
          trigger_params.minute = $('#input-job-minute').val();
        } else if(trigger.toLowerCase() == "interval"){
          trigger_params.days = parseInt($('#input-job-days').val());
          trigger_params.hours = parseInt($('#input-job-hours').val());
          trigger_params.minutes = parseInt($('#input-job-minutes').val());
          trigger_params.seconds = parseInt($('#input-job-seconds').val());
        }


        if (!$.trim(jobName)) {
          utils.alertError('Please fill in job name');
          return;
        }

        if (!$.trim(jobTask)) {
          utils.alertError('Please fill in job task class');
          return;
        }

        // In order to pass space via command line arguments, we replace space
        // with $, and replace $ back to space. So, '$' is reserved and can't
        // be used in user input.
        if (jobName.indexOf('$') != -1 ||
            jobTask.indexOf('$') != -1 ||
            args.indexOf('$') != -1) {
          utils.alertError('You cannot use "$". Please remove it.');
          return;
        }

        var taskArgs = [];
        try {
          taskArgs = utils.getTaskArgs(args);
        } catch (err) {
          utils.alertError('Invalid Arguments. Should be valid JSON string,' +
              ' e.g., [1, 2, "hello"].');
          return;
        }

        this.collection.addJob({
          job_class_string: jobTask,
          name: jobName,
          pub_args: taskArgs,
          trigger: trigger,
          trigger_params: trigger_params
        });

        $('#add-job-modal').modal('hide');
      }, this));
    }
  });
});
