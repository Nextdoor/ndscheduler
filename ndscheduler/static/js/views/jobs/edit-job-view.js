/**
 * edit-job view.
 *
 * @author wenbin@nextdoor.com
 */

require.config({
  paths: {
    'jquery': 'vendor/jquery',
    'underscore': 'vendor/underscore',
    'backbone': 'vendor/backbone',
    'bootstrap': 'vendor/bootstrap',
    'bootstrapswitch': 'vendor/bootstrap-switch',

    'utils': 'utils',

    'text': 'vendor/text',
    'edit-job-modal': 'templates/edit-job.html',
    'job-class-notes': 'templates/job-class-notes.html'
  },

  shim: {
    'bootstrapswitch': {
      deps: ['bootstrap']
    },

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
        'text!edit-job-modal',
        'text!job-class-notes',
        'backbone',
        'bootstrapswitch'], function(utils, EditJobModalHtml, JobClassNotesHtml) {

  'use strict';

  return Backbone.View.extend({
    initialize: function() {
      $('body').append(EditJobModalHtml);

      var jobsMetaInfo = $.parseJSON($('#jobs-meta-info').html());
      var data = [];
      _.forEach(jobsMetaInfo, function(job) {
        data.push({
          id: job.job_class_string,
          text: job.job_class_string,
          job: job
        })
      });
      $('#edit-input-job-task-class').select2({
        data: data
      }).on("select2-selecting", function(e) {
        $('#edit-job-class-notes').html(
            _.template(JobClassNotesHtml)({job: e.choice.job})
        );
      });

      // Load notes of job class during opening of modal dialog
      $('#edit-input-job-task-class').select2({
        data: data
      }).on("change", function(e) {

        var job_name = e.target.value;

        var job = data.find(function(e){
          return e.id === job_name;
        });
        $('#edit-job-class-notes').html(
            _.template(JobClassNotesHtml)({job: job.job})
        );
      });

      this.bindJobTriggerTabChangedEvent();
      this.bindEditJobConfirmClickEvent();
      this.bindDeleteJobConfirmClickEvent();
      this.bindModalPopupEvent();
    },

    /**
     * Bind click event for delete-job button.
     */
    bindDeleteJobConfirmClickEvent: function() {
      var $button = $('#delete-job-confirm-button');
      $button.off('click');
      $button.on('click', _.bind(function() {
        if (confirm('Really want to delete it?')) {
          var jobId = $('#edit-input-job-id').val();
          this.collection.deleteJob(jobId);
          $('#edit-job-modal').modal('hide');
        }
      }, this));
    },

    /**
     * Bind popup event for edit-job modal.
     */
    bindModalPopupEvent: function() {
      $('#edit-job-modal').on('show.bs.modal', _.bind(function(e) {
        var $button = $(e.relatedTarget);
        var jobId = $button.data('id');
        var jobActive = $button.data('job-active');
        var trigger = $button.data('job-trigger').toLowerCase();
        var trigger_params = $button.data('job-trigger-params');

        $('#edit-input-job-name').val($button.data('job-name'));
        $('#edit-input-job-task-class').val($button.data('job-task')).trigger('change');
        $('#edit-input-job-task-args').val($button.attr('data-job-pubargs'));
        $('#edit-input-job-id').val(jobId);
        $('#edit-job-trigger').val(trigger);


        if(trigger == "cron"){
          $('#edit-job-month').val(trigger_params.month);
          $('#edit-job-day-of-week').val(trigger_params.day_of_week);
          $('#edit-job-day').val(trigger_params.day);
          $('#edit-job-hour').val(trigger_params.hour);
          $('#edit-job-minute').val(trigger_params.minute);
        } else if (trigger === "interval"){
          let interval_obj = secondsToObj(trigger_params.interval);
          $('#edit-job-seconds').val(interval_obj.seconds);
          $('#edit-job-minutes').val(interval_obj.minutes);
          $('#edit-job-hours').val(interval_obj.hours);
          $('#edit-job-days').val(interval_obj.days);
        }

        $('#edit-trigger-tab a[href="#edit-'+trigger+'-sched"]').tab('show');


        var $checkbox = $('<input>', {
          type: 'checkbox',
          name: 'pause-resume-checkbox',
          id: 'pause-resume-checkbox',
          checked: ''
        });
        $('#pause-resume-container').html($checkbox);
        $("[name='pause-resume-checkbox']").bootstrapSwitch({
          'onText': 'Active',
          'offText': 'Inactive',
          'state': (jobActive == 'yes'),
          'onSwitchChange': _.bind(function(event, state) {
            if (state) {
              this.collection.resumeJob(jobId);
            } else {
              this.collection.pauseJob(jobId);
            }
            $('#edit-job-modal').modal('hide');
          }, this)
        });
      }, this));
    },

    bindJobTriggerTabChangedEvent: function() {
      $('#edit-trigger-tab a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        //show selected tab / active
        var trigger = $(e.target).attr('id');
        $('#edit-job-trigger').val(trigger);
      });

    },


    /**
     * Bind click event for edit-job modal.
     */
    bindEditJobConfirmClickEvent: function() {
      var editConfirmButton = $('#edit-job-confirm-button').off('click');
      editConfirmButton.on('click', _.bind(function(e) {
        e.preventDefault();

        var jobId = $('#edit-input-job-id').val();
        var jobName = $('#edit-input-job-name').val();
        var jobTask = $('#edit-input-job-task-class').val();
        var args = $('#edit-input-job-task-args').val();
        var trigger = $('#edit-job-trigger').val();
        var trigger_params = {};

        if(trigger == 'cron') {
          trigger_params.month = $('#edit-job-month').val();
          trigger_params.day_of_week = $('#edit-job-day-of-week').val();
          trigger_params.day = $('#edit-job-day').val();
          trigger_params.hour = $('#edit-job-hour').val();
          trigger_params.minute = $('#edit-job-minute').val();

        } else if(trigger == 'interval') {
          var seconds = parseInt($('#edit-job-seconds').val());
          var minutes = parseInt($('#edit-job-minutes').val());
          var hours = parseInt($('#edit-job-hours').val());
          var days = parseInt($('#edit-job-days').val());

          var interval_seconds = 86400 * days + 3600 * hours + 60 * minutes + seconds;

          trigger_params.interval = interval_seconds;
        }

        if (jobName.trim() === '') {
          utils.alertError('Please fill in job name');
          return;
        }

        if (jobTask.trim() === '') {
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

        var taskArgs = undefined;
        try {
          taskArgs = utils.getTaskArgs(args);
        } catch (err) {
          utils.alertError('Invalid Arguments. Should be valid JSON string,' +
              ' e.g., [1, 2, "hello"].');
          return;
        }

        // TODO (wenbin): more checking for cron string
        this.collection.modifyJob(jobId, {
          job_class_string: jobTask,
          name: jobName,
          pub_args: taskArgs,
          trigger: trigger,
          trigger_params: trigger_params
        });

        $('#edit-job-modal').modal('hide');
      }, this));
    }
  });
});
