/**
 * run-job view.
 *
 * @author wenbin@nextdoor.com
 */

require.config({
  paths: {
    'jquery': 'vendor/jquery',
    'underscore': 'vendor/underscore',
    'backbone': 'vendor/backbone',
    'bootstrap': 'vendor/bootstrap',

    'text': 'vendor/text',
    'run-job-modal': 'templates/run-job.html'
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

define(['text!run-job-modal',
        'backbone',
        'bootstrap'], function(RunJobModalHtml) {
  'use strict';

  return Backbone.View.extend({
    initialize: function() {
      $('body').append(RunJobModalHtml);

      this.bindRunJobConfirmClickEvent();
      this.bindModalPopupEvent();
    },

    /**
     * Bind popup event for run-job modal.
     */
    bindModalPopupEvent: function() {
      $('#run-job-modal').on('show.bs.modal', _.bind(function(e) {
        var customRunButton = $(e.relatedTarget);
        $('#run-job-name').text(customRunButton.attr('data-job-name'));
        $('#run-job-task').text(customRunButton.attr('data-job-task'));
        $('#run-job-pubargs').text(customRunButton.attr('data-job-pubargs'));
        $('#run-job-confirm-button').data('id', customRunButton.data('id'));
      }, this));
    },

    /**
     * Bind click event for run-job-confirm button.
     */
    bindRunJobConfirmClickEvent: function() {
      var runJobButton = $('#run-job-confirm-button').off('click');
      runJobButton.on('click', _.bind(function(e) {
        e.preventDefault();
        var jobId = $(e.target).data('id');
        this.collection.runJob(jobId);
        $('#run-job-modal').modal('hide');
      }, this));
    }
  });
});
