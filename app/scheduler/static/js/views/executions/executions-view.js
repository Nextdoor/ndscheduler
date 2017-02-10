/**
 * Executions view.
 *
 * @author wenbin@nextdoor.com
 */

require.config({
  paths: {
    'jquery': 'vendor/jquery',
    'underscore': 'vendor/underscore',
    'backbone': 'vendor/backbone',
    'bootstrap': 'vendor/bootstrap',

    'executions-filter-view': 'views/executions/filter-view',
    'executions-stats-view': 'views/executions/stats-view',
    'executions-table-view': 'views/executions/table-view'
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

define(['executions-filter-view',
        'executions-stats-view',
        'executions-table-view',
        'backbone',
        'bootstrap'], function(ExecutionsFilterView,
                               ExecutionsStatsView,
                               ExecutionsTableView) {

  'use strict';

  return Backbone.View.extend({
    initialize: function() {
      // Subview 1: Filter.
      new ExecutionsFilterView({
        collection: this.collection
      });

      // Subview 2: Statistics.
      new ExecutionsStatsView({
        collection: this.collection
      });

      // Subview 3: Executions table.
      new ExecutionsTableView({
        collection: this.collection
      });
    }
  });
});
