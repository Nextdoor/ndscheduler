/**
 * Audit Log Model
 *
 * @author wenbin@nextdoor.com
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
     * Returns html string for job name in logs.
     *
     * @return {string} html string for job name.
     */
    getJobNameHTMLString: function() {
      var jobName = this.get('job_name'),
          jobId = this.get('job_id');
      return '<a href="/#jobs/' + jobId + '">' + jobName + '</a>';
    },

    /**
     * Returns html string for log event type.
     *
     * @return {string} html string for log event type.
     */
    getEventHTMLString: function() {
      var event = this.get('event');
      var style = 'added-color';
      if (event === 'added') {
        style = 'added-color';
      } else if (event === 'custom_run') {
        style = 'custom-run-color';
      } else if (event === 'paused') {
        style = 'paused-color';
      } else if (event === 'resumed') {
        style = 'resumed-color';
      } else if (event === 'deleted') {
        style = 'deleted-color';
      } else if (event === 'modified') {
        style = 'modified-color';
      }
      return '<span class="' + style + '">' + event + '</span>';
    },

    /**
     * Returns event time string.
     *
     * @return {string} event time string.
     */
    getEventTimeString: function() {
      var createdAt = this.get('created_time');
      return moment(createdAt).format('MM/DD/YYYY HH:mm:ss Z');
    },

    /**
     * Returns string for event description.
     *
     * @return {string} string for event description.
     */
    getDescriptionHTMLString: function() {
      var desc = this.get('description');
      var event = this.get('event');
      var descHtml = '';
      if (event === 'custom_run') {
        // TODO (wenbin): Make a beautiful popup window to display this info,
        // instead of linking to raw json.
        descHtml = 'Execution ID: <a href="/#executions/' +
            desc + '">' + desc + '</a>';
      } else if (event === 'modified') {
        descHtml = 'diff: old val => new val <br>' + desc;
      }

      return descHtml;
    }
  });
});
