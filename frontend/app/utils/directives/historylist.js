angular.module('app.utils.directives').directive('historyList', HistoryListDirective);

HistoryListDirective.$inject = ['$filter', '$http', '$modal', '$q', '$state', 'EmailAccount', 'Note', 'NoteDetail', 'CaseDetail', 'DealDetail','EmailDetail'];
function HistoryListDirective ($filter, $http, $modal, $q, $state, EmailAccount, Note, NoteDetail, CaseDetail, DealDetail, EmailDetail) {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            target: '=',
            object: '='
        },
        templateUrl: 'utils/directives/historylist.html',
        link: function (scope, element, attrs) {
            var noteTargets = ['account', 'contact', 'deal', 'case'];
            var caseTargets = ['account', 'contact'];
            var dealTargets = ['account'];
            var emailTargets = ['account', 'contact'];
            var page = 0;
            var pageSize = 15;

            scope.history = {};
            scope.history.list = [];
            scope.history.types = {
                '': {name: 'All', visible: true},
                'note': {name: 'Notes', visible: false},
                'case': {name: 'Cases',visible: false},
                'deal': {name: 'Deals', visible: false},
                'email': {name: 'Emails', visible: false}
            };
            scope.history.activeFilter = '';
            scope.history.showMoreText = 'Show more';
            scope.history.loadMore = loadMore;
            scope.history.reloadHistory = reloadHistory;
            scope.history.addNote = addNote;
            scope.history.editNote = editNote;
            scope.history.deleteNote = deleteNote;

            scope.note = {};
            scope.note.type = 0;

            activate();

            ////////

            function activate() {
                // Somehow calling autosize on page content load does not work
                // in the historylist.
                autosize($('textarea'));
                loadMore();
            }

            function loadMore() {
                if (!scope.object.$resolved) {
                    scope.object.$promise.then(function(obj) {
                        _fetchHistory(obj);
                    })
                } else {
                    _fetchHistory(scope.object);
                }
            }

            function reloadHistory() {
                page -= 1;
                loadMore();
            }

            function _fetchHistory(obj) {
                var history = [];
                var promises = [];
                page += 1;
                var neededLength = page * pageSize;
                var requestLength = neededLength + 1;

                // Check if we need to fetch notes
                if (noteTargets.indexOf(scope.target) != -1) {
                    var notePromise = NoteDetail.query({filterquery: 'content_type:' + scope.target + ' AND object_id:' + obj.id, size: requestLength }).$promise;
                    promises.push(notePromise);  // Add promise to list of all promises for later handling

                    notePromise.then(function(results) {
                        results.forEach(function(note) {
                            history.push(note);
                        });
                    });
                }

                // Check if we need to fetch cases
                if (caseTargets.indexOf(scope.target) != -1) {
                    var casePromise = CaseDetail.query({filterquery: scope.target + ':' + obj.id, size: requestLength}).$promise;
                    promises.push(casePromise);  // Add promise to list of all promises for later handling

                    casePromise.then(function(results) {
                        results.forEach(function(caseItem) {
                            history.push(caseItem);
                            NoteDetail.query({filterquery: 'content_type:case AND object_id:' + caseItem.id, size: 5})
                                .$promise.then(function(notes) {
                                    caseItem.notes = notes;
                                });
                        });
                    });
                }

                // Check if we need to fetch deals
                if (dealTargets.indexOf(scope.target) != -1) {
                    var dealPromise = DealDetail.query({filterquery: scope.target + ':' + obj.id, size: requestLength}).$promise;
                    promises.push(dealPromise);  // Add promise to list of all promises for later handling

                    dealPromise.then(function(results) {
                        results.forEach(function(deal) {
                            NoteDetail.query({
                                filterquery: 'content_type:deal AND object_id:' + deal.id,
                                size: 5
                            }).$promise.then(function (notes) {
                                    deal.notes = notes;
                                });
                            history.push(deal);
                        });
                    });
                }

                // Check if we need to fetch emails
                if (emailTargets.indexOf(scope.target) != -1) {
                    var tenantEmailAccountPromise = EmailAccount.query().$promise;
                    promises.push(tenantEmailAccountPromise); // Add tenant email query to promises list

                    var emailPromise;
                    if (scope.target == 'account') {
                        emailPromise = EmailDetail.query({account_related: obj.id, size: requestLength}).$promise;
                    } else {
                        emailPromise = EmailDetail.query({contact_related: obj.id, size: requestLength}).$promise;
                    }
                    promises.push(emailPromise);  // Add promise to list of all promises for later handling

                    $q.all([tenantEmailAccountPromise, emailPromise]).then(function(results) {
                        var tenantEmailAccountList = results[0];
                        var emailMessageList = results[1];

                        emailMessageList.forEach(function(email) {
                            tenantEmailAccountList.forEach(function (emailAddress) {
                                if (emailAddress.email_address === email.sender_email) {
                                    email.right = true;
                                }
                            });
                            history.push(email);
                        });
                    });
                }

                // Get all history types and add them to a common history
                $q.all(promises).then(function() {
                    var orderedHistoryList = [];

                    // Order our current historylist
                    $filter('orderBy')(history, 'date', true).forEach(function(item) {
                        // We have on of these items so we need to be able to filter on it
                        scope.history.types[item.historyType].visible = true;

                        // Push our item to our ordered list
                        orderedHistoryList.push(item);
                    });
                    if (!orderedHistoryList) {
                        // Make sure the max size of the list doesn't grow each click
                        page -= 1;

                        // Set the button text to inform the user what's happening
                        scope.history.showMoreText = 'No history (refresh)';
                    }
                    else if (orderedHistoryList.length <= neededLength) {
                        // Make sure the max size of the list doesn't grow each click
                        page -= 1;

                        // Set the button text to inform the user what's happening
                        scope.history.showMoreText = 'End reached (refresh)';
                    }

                    // Set the historylist to our new list
                    scope.history.list = orderedHistoryList.slice(0, neededLength);
                });
            }

            function addNote(note) {
                $http({
                    method: 'POST',
                    url: '/notes/create/',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    data: $.param({
                        content: note.content,
                        type: note.type,
                        content_type: scope.target,
                        object_id: scope.object.id
                    })
                }).success(function() {
                    $state.go($state.current, {}, {reload: true});
                });
            }

            function editNote(note) {
                var modalInstance = $modal.open({
                    templateUrl: 'utils/controllers/note_edit.html',
                    controller: 'EditNoteModalController',
                    size: 'lg',
                    resolve: {
                        note: function() {
                            return note;
                        }
                    }
                });

                modalInstance.result.then(function() {
                    $state.go($state.current, {}, {reload: true});
                });
            }

            function deleteNote(note) {
                if (confirm('Are you sure?')) {
                    Note.delete({
                        id:note.id
                    }, function() {  // On success
                        var index = scope.history.list.indexOf(note);
                        scope.history.list.splice(index, 1);
                    }, function(error) {  // On error
                        alert('something went wrong.')
                    });
                }
            }
        }
    }
}

