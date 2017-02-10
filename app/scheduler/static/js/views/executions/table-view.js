/**
 * executions-table view.
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
    'text': 'vendor/text',
    'execution-stacktrace': 'templates/execution-stacktrace.html'
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
        'text!execution-stacktrace',
        'backbone',
        'bootstrap',
        'datatables'], function(utils, ExecutionStacktraceHtml) {
  'use strict';

  return Backbone.View.extend({
    initialize: function() {
      $('body').append(ExecutionStacktraceHtml);

      this.listenTo(this.collection, 'sync', this.render);
      this.listenTo(this.collection, 'request', this.requestRender);
      this.listenTo(this.collection, 'error', this.requestError);

      this.table = $('#executions-table').dataTable({
        // Sorted by last updated time
        'order': [[3, 'desc']]
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
     * Event handler for starting to send network request.
     */
    requestRender: function() {
      this.table.fnClearTable();
      this.spinner = utils.startSpinner('executions-spinner');
    },

    /**
     * Event handler for finishing fetching execution data.
     */
    render: function() {
      var executions = this.collection.executions;

      var data = [];
      _.each(executions, function(execution) {
        data.push([
          execution.getNameHTMLString(),
          execution.getStatusHTMLString(),
          execution.getScheduledAtString(),
          execution.getFinishedAtString(),
          execution.getDescription()
        ]);
      });

      if (data.length) {
        this.table.fnClearTable();
        this.table.fnAddData(data);

        var buttons = $('[data-action=show-full-stacktrace]');
        _.each(buttons, function(btn) {
          $(btn).on('click', _.bind(function(e) {
            e.preventDefault();
            $('#stacktrace-box').text(decodeURI($(e.target).data('content')));
            $('#execution-stacktrace-modal').modal();
          }, this));

          // If there's a query parameter stacktrace, we'll display the stack trace.
          if (!_.isUndefined(utils.getParameterByName('stacktrace'))) {
            $('#stacktrace-box').text(executions[0].get('description'));
            $('#execution-stacktrace-modal').modal();
          }
        });
      }

      utils.stopSpinner(this.spinner);
    }
  });
});
