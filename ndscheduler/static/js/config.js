/**
 * Configurations / constants
 *
 */

define([], function() {

  'use strict';

  var urlPrefix = '/api/v2';

  return {
    'jobs_url': urlPrefix + '/jobs',
    'executions_url': urlPrefix + '/executions',
    'logs_url': urlPrefix + '/logs',
    'scheduler_url': urlPrefix + '/scheduler'
  };
});
