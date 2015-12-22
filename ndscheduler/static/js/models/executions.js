/**
 * Executions collection
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
    'executionModel': 'models/execution'
  },

  shim: {
    'backbone': {
      deps: ['underscore', 'jquery'],
      exports: 'Backbone'
    }
  }
});

define(['utils',
        'executionModel',
        'config',
        'backbone'], function(utils, ExecutionModel, config) {
  return Backbone.Collection.extend({

    /**
     * Fetches number of all executions.
     */
    getTotalCount: function() {
      return this.executions.length;
    },

    /**
     * Fetches number of all executions with certain state.
     *
     * @param {string} state the state of execution, which can only be one
     *   of the following strings: scheduled, running, stopping, stopped,
     *   failed, succeeded, timeout, scheduled error.
     */
    getCount: function(state) {
      return _.filter(this.executions, function(execution) {
        return execution.get('state') == state }).length;
    },

    /**
     * Fetches executions.
     */
    getExecutions: function() {
      // Default, pull latest 10 minutes
      this.url = config.executions_url;
      this.fetch();
    },

    /**
     * Fetches an execution.
     *
     * @param {string} executionId id of the execution we want to fetch.
     */
    getExecution: function(executionId) {
      this.url = config.executions_url + '/' + executionId;
      this.fetch();
    },

    /**
     * Fetches executions within a time range.
     *
     * @param {string} start starting time in UTC and in iso8601 format.
     * @param {string} end ending time in UTC and in iso8601 format.
     */
    getExecutionsByRange: function(start, end) {
      this.url = config.executions_url + '?time_range_end=' + end +
          '&time_range_start=' + start;
      this.fetch();
    },

    /**
     * Parses response from scheduler api server.
     *
     * @param {object} response the response returned from api server.
     * @return {array} an array of objects of ExecutionModel.
     */
    parse: function(response) {
      var executions = response.executions;

      // If api server returns a single execution, then make an array here.
      if (!executions) {
        executions = [response];
      }
      this.executions = [];
      _.each(executions, function(execution) {
        this.executions.push(new ExecutionModel(execution));
      }, this);
      return this.executions;
    }
  });
});
