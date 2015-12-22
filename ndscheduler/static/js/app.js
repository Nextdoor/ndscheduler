require.config({
  urlArgs: 'bust=' + cacheBuster,
  baseUrl: '/static/js',
  paths: {
    'jquery': 'vendor/jquery',
    'backbone': 'vendor/backbone',
    'underscore': 'vendor/underscore',

    'jobs-view': 'views/jobs/jobs-view',
    'executions-view': 'views/executions/executions-view',
    'logs-view': 'views/logs/logs-view',

    'jobs-collection': 'models/jobs',
    'executions-collection': 'models/executions',
    'logs-collection': 'models/logs'
  },

  shim: {
    'backbone': {
      deps: ['underscore', 'jquery'],
      exports: 'Backbone'
    }
  }
});

require(['jobs-view',
  'executions-view',
  'logs-view',
  'jobs-collection',
  'executions-collection',
  'logs-collection',
  'backbone'], function(JobsView,
                        ExecutionsView,
                        LogsView,
                        JobsCollection,
                        ExecutionsCollection,
                        LogsCollection) {
  'use strict';

  var jobsCollection = new JobsCollection();
  var executionsCollection = new ExecutionsCollection();
  var logsCollection = new LogsCollection();

  new JobsView({
    collection: jobsCollection
  });

  new ExecutionsView({
    collection: executionsCollection
  });

  new LogsView({
    collection: logsCollection
  });

  //
  // Initialize URL router
  //
  var AppRouter = Backbone.Router.extend({
    routes: {
      'jobs': 'jobsRoute',
      'executions': 'executionsRoute',
      'jobs/:jid': 'jobsRoute',
      'executions/:eid': 'executionsRoute',
      'logs': 'logsRoute',
      '*actions': 'defaultRoute'
    }
  });

  var switchTab = function(switchTo) {
    var pages = ['jobs', 'executions', 'logs'];
    _.each(pages, function(page) {
      $('#' + page + '-page-sidebar').hide();
      $('#' + page + '-page-content').hide();
      $('#' + page + '-tab').removeClass();
    });
    $('#' + switchTo + '-page-sidebar').show();
    $('#' + switchTo + '-page-content').show();
    $('#' + switchTo + '-tab').addClass('active');
  };

  var appRouter = new AppRouter;
  appRouter.on('route:jobsRoute', function(jobId) {
    switchTab('jobs');
    if (jobId) {
      jobsCollection.getJob(jobId);
    } else {
      jobsCollection.getJobs();
    }
  });

  appRouter.on('route:executionsRoute', function(executionId) {
    switchTab('executions');

    if (executionId) {
      executionsCollection.getExecution(executionId);
    } else {
      executionsCollection.getExecutions();
    }
  });

  appRouter.on('route:logsRoute', function() {
    switchTab('logs');
    logsCollection.getLogs();
  });

  appRouter.on('route:defaultRoute', function(actions) {
    // Anything else defaults to jobs view
    switchTab('jobs');
    jobsCollection.getJobs();
  });

  Backbone.history.start();
});
