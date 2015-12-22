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

    'utils': 'utils',

    'text': 'vendor/text',
    'add-job-modal': 'templates/add-job.html'
  },

  shim: {
    'bootstrap': {
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
  'backbone',
  'bootstrap'], function(utils, AddJobModalHtml) {

  'use strict';

  return Backbone.View.extend({
    initialize: function() {
      $('body').append(AddJobModalHtml);

      this.bindAddJobConfirmClickEvent();
    },

    bindAddJobConfirmClickEvent: function() {

      $('#add-job-confirm-button').on('click', _.bind(function(e) {
        e.preventDefault();

        var jobName = $('#input-job-name').val();
        var jobTask = $('#input-job-task-class').val();
        var month = $('#input-job-month').val();
        var dayOfWeek = $('#input-job-day-of-week').val();
        var day = $('#input-job-day').val();
        var hour = $('#input-job-hour').val();
        var minute = $('#input-job-minute').val();
        var args = $('#input-job-task-args').val();
        var languages = $('#input-job-languages').val();

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
          month: month,
          day_of_week: dayOfWeek,
          day: day,
          hour: hour,
          minute: minute
        });

        $('#add-job-modal').modal('hide');
      }, this));
    }
  });
});
