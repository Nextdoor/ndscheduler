/**
 * executions-stats view.
 *
 * @author wenbin@nextdoor.com
 */

require.config({
  paths: {
    'jquery': 'vendor/jquery',
    'underscore': 'vendor/underscore',
    'backbone': 'vendor/backbone',
    'bootstrap': 'vendor/bootstrap'
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

define(['backbone', 'bootstrap'], function() {
  'use strict';

  return Backbone.View.extend({
    initialize: function() {
      this.listenTo(this.collection, 'sync', this.render);
    },

    /**
     * Event handler for finishing fetching executions data.
     */
    render: function() {
      $('#executions-total-count').text(this.collection.getTotalCount());
      $('#executions-scheduled-count').text(
          this.collection.getCount('scheduled'));
      $('#executions-running-count').text(this.collection.getCount('running'));
      $('#executions-scheduled-error-count').text(
          this.collection.getCount('scheduled error'));
      $('#executions-failed-count').text(this.collection.getCount('failed'));
      $('#executions-success-count').text(
          this.collection.getCount('succeeded'));
    }
  });
});
