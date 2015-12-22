/**
 * jobs-stats view.
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
     * Event handler for finishing fetching jobs data.
     */
    render: function() {
      $('#jobs-total-count').text(this.collection.getTotal());
      $('#jobs-active-count').text(this.collection.getActiveCount());
      $('#jobs-inactive-count').text(this.collection.getInactiveCount());
    }
  });
});
