/**
 * Execution model
 */

require.config({
  paths: {
    'jquery': 'vendor/jquery',
    'underscore': 'vendor/underscore',
    'backbone': 'vendor/backbone',
    'moment': 'vendor/moment',

    'config': 'config'
  },

  shim: {
    'backbone': {
      deps: ['underscore', 'jquery'],
      exports: 'Backbone'
    }
  }
});

define(['config',
        'backbone',
        'vendor/moment-timezone-with-data'], function(config, backbone, moment) {
  'use strict';

  return Backbone.Model.extend({

    /**
     * Returns the html string for job name of this execution.
     *
     * @return {string} html string for job name of this execution.
     */
    getNameHTMLString: function() {
      var jobId = this.get('job').job_id,
          executionId = this.get('execution_id');

      var jobName = '';
      try {
        jobName = this.get('job')['name'];
      } catch (e) {
        jobName = '<span class="failed-color">Unknown Job</span>';
      }

      return '<a href="/#executions/' + executionId +
          '"><i class="fa fa-link fa-lg"></i></a> <a href="/#jobs/' + jobId +
          '">' + jobName + '</a>';
    },

    /**
     * Returns the html string for this execution's status.
     *
     * @return {string} html string for execution status.
     */
    getStatusHTMLString: function() {
      var state = this.get('state');
      var style = 'scheduled-color';
      if (state === 'scheduled error') {
        style = 'scheduled-error-color';
      } else if (state === 'running') {
        style = 'running-color';
      } else if (state === 'succeeded') {
        style = 'success-color';
      } else if (state === 'failed') {
        style = 'failed-color';
      }
      return '<span class="' + style + '">' + state + '</span>';
    },

    /**
     * Returns the scheduled time string.
     *
     * @return {string} scheduled time string.
     */
    getScheduledAtString: function() {
      return moment(this.get('scheduled_time')).local().format(
          'MM/DD/YYYY HH:mm:ss Z');
    },

    /**
     * Returns the finished time string.
     *
     * @return {string} finished time string.
     */
    getFinishedAtString: function() {
      return moment(this.get('updated_time')).local().format(
          'MM/DD/YYYY HH:mm:ss Z');
    },

    /**
     * Returns html string for execution description.
     *
     * @return {string} html string for taskworker information.
     */
    getDescription: function() {
      var state = this.get('state');
      if (state === 'scheduled error') {
        return ('<span class="italic"><a href="#" data-content="' +
          encodeURI(this.get('description')) +
          '" data-action="show-full-stacktrace">Full Stacktrace</a></span>');
      } else if (state === 'failed') {
        return ('hostname: ' + this.get('hostname') + 'pid:' + this.get('pid') +
          '<br><span class="italic"><a href="#" data-content="' +
          encodeURI(this.get('description')) +
          '" data-action="show-full-stacktrace">Full Stacktrace</a></span>');
      } else {
        return this.get('description');
      }
    }
  });
});
