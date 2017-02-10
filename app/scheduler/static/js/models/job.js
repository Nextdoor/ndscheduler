/**
 * Job Model
 *
 * @author wenbin@nextdoor.com
 */

require.config({
  paths: {
    'jquery': 'vendor/jquery',
    'underscore': 'vendor/underscore',
    'backbone': 'vendor/backbone',
    'moment': 'vendor/moment'
  },

  shim: {
    'backbone': {
      deps: ['underscore', 'jquery'],
      exports: 'Backbone'
    }
  }
});

define(['backbone', 'vendor/moment-timezone-with-data'], function(backbone, moment) {
  'use strict';

  return Backbone.Model.extend({

    /**
     * Returns schedule string for this job.
     *
     * @return {string} schedule string for this job.
     */
    getScheduleString: function() {
      return 'minute: ' + this.get('minute') + ', hour: ' + this.get('hour') +
          ', day: ' + this.get('day') + ', month: ' + this.get('month') +
          ', day of week: ' + this.get('day_of_week');
    },

    /**
     * Returns json string for arguments to run the job.
     *
     * @return {string} a json string for arguments to run this job.
     */
    getPubArgsString: function() {
      return JSON.stringify(this.get('pub_args'));
    },

    /**
     * Returns html string for next run time of this job.
     *
     * @return {string} html string for next run time of this job.
     */
    getNextRunTimeHTMLString: function() {
      var nextRunTime = this.get('next_run_time');
      var returnString = '';
      if (!nextRunTime) {
        returnString = '<span class="failed-color">Inactive</span>';
      } else {
        var tz = $('#display-tz').val();
        returnString = '<span class="success-color">' + moment().format('Z') + ': ' +
            moment(nextRunTime).format('MM/DD/YYYY HH:mm:ss') +
            '</span><br><span class="scheduled-color">UTC: ' +
            moment(nextRunTime).utc().format('MM/DD/YYYY HH:mm:ss') +
            '</span>';
      }
      return returnString;
    },

    /**
     * Returns string to indicate whether or not this job is active.
     *
     * @return {string} "yes" or "no".
     */
    getActiveString: function() {
      var nextRunTime = this.get('next_run_time');
      return nextRunTime ? 'yes' : 'no';
    }
  });
});
