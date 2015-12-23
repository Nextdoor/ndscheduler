/**
 * Jobs view.
 *
 * @author wenbin@nextdoor.com
 */

require.config({
  paths: {
    'jquery': 'vendor/jquery',
    'underscore': 'vendor/underscore',
    'backbone': 'vendor/backbone',
    'bootstrap': 'vendor/bootstrap',

    'add-job-view': 'views/jobs/add-job-view',
    'jobs-stats-view': 'views/jobs/stats-view',
    'jobs-table-view': 'views/jobs/table-view'

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

define(['add-job-view',
        'jobs-stats-view',
        'jobs-table-view',
        'backbone',
        'bootstrap'], function(AddJobView, JobsStatsView, JobsTableView) {

  'use strict';

  return Backbone.View.extend({
    initialize: function() {
      // Subview 1: Add Job.
      new AddJobView({
        collection: this.collection
      });

      // Subview 2: Statistics.
      new JobsStatsView({
        collection: this.collection
      });

      // Subview 3: Jobs table.
      new JobsTableView({
        collection: this.collection
      });
    }
  });
});
