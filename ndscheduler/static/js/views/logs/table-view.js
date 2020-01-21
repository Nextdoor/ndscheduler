/**
 * logs-table view.
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

    'utils': 'utils'
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
        'backbone',
        'bootstrap',
        'datatables'], function(utils) {

  'use strict';

  return Backbone.View.extend({

    initialize: function() {
      this.listenTo(this.collection, 'sync', this.render);
      this.listenTo(this.collection, 'request', this.requestRender);
      this.listenTo(this.collection, 'reset', this.resetRender);

      // Initialize data table
      this.table = $('#logs-table').dataTable({
        // Sorted by job name
        'order': [[3, 'desc']],
        "iDisplayLength": 25
      });
    },

    /**
     * Event handler for starting to make network request.
     */
    requestRender: function() {
      this.table.fnClearTable();
      this.spinner = utils.startSpinner('logs-spinner');
    },

    /**
     * Event handler for resetting logs data.
     */
    resetRender: function() {
      // It'll trigger sync event
      this.collection.getLogs();
    },

    /**
     * Event handler for finishing fetching jobs data.
     */
    render: function() {
      var logs = this.collection.logs;

      var data = [];

      // Build up data to pass to data tables
      _.each(logs, function(log) {
        var logObj = log.toJSON();
        data.push([
          log.getJobNameHTMLString(),
          log.getEventHTMLString(),
          logObj.user,
          log.getEventTimeString(),
          log.getDescriptionHTMLString()
        ]);
      });

      if (data.length) {
        this.table.fnAddData(data);
      }

      // Stop the spinner
      this.spinner.stop();
    }
  });
});
