/**
 * Logs view.
 *
 * @author wenbin@nextdoor.com
 */

require.config({
  paths: {
    'jquery': 'vendor/jquery',
    'underscore': 'vendor/underscore',
    'backbone': 'vendor/backbone',
    'bootstrap': 'vendor/bootstrap',

    'logs-filter-view': 'views/logs/filter-view',
    'logs-table-view': 'views/logs/table-view'
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

define(['logs-filter-view',
        'logs-table-view',
        'backbone',
        'bootstrap'], function(LogsFilterView, LogsTableView) {

  'use strict';

  return Backbone.View.extend({
    initialize: function() {
      // Subview 1: Filter.
      new LogsFilterView({
        collection: this.collection
      });

      // Subview 2: Logs table
      new LogsTableView({
        collection: this.collection
      });
    }
  });
});
