/**
 * Logs collection
 *
 * @author wenbin@nextdoor.com
 *
 */

require.config({
  paths: {
    'jquery': 'vendor/jquery',
    'underscore': 'vendor/underscore',
    'backbone': 'vendor/backbone',

    'utils': 'utils',
    'config': 'config',
    'logModel': 'models/log'
  },

  shim: {
    'backbone': {
      deps: ['underscore', 'jquery'],
      exports: 'Backbone'
    }
  }
});

define(['utils',
        'logModel',
        'config',
        'backbone'], function(utils, LogModel, config) {
  return Backbone.Collection.extend({

    /**
     * Fetches logs.
     */
    getLogs: function() {
      // Default, pull latest 10 minutes
      this.url = config.logs_url;
      this.fetch();
    },

    /**
     * Fetches logs in a certain time range.
     *
     * @param {string} start starting time in UTC and in iso8601 format.
     * @param {string} end ending time in UTC and in iso8601 format.
     */
    getLogsByRange: function(start, end) {
      this.url = config.logs_url + '?time_range_end=' + end +
          '&time_range_start=' + start;
      this.fetch();
    },

    /**
     * Parses response from scheduler api server.
     *
     * @param {object} response the response returned from api server.
     * @return {Array} an array of objects of LogModel.
     */
    parse: function(response) {
      var logs = response.logs;

      this.logs = [];
      _.each(logs, function(log) {
        this.logs.push(new LogModel(log));
      }, this);
      return this.logs;
    }
  });
});
