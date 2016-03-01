angular.module('app.utils.directives').directive('historyList', HistoryListDirective);

HistoryListDirective.$inject = ['$filter', '$http', '$uibModal', '$q', '$state', 'EmailAccount',
'Note', 'NoteDetail', 'Case', 'DealDetail', 'EmailDetail'];
function HistoryListDirective($filter, $http, $uibModal, $q, $state, EmailAccount,
Note, NoteDetail, Case, DealDetail, EmailDetail) {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            target: '=',
            object: '=',
        },
        templateUrl: 'utils/directives/historylist.html',
        link: function(scope, element, attrs) {
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
                'case': {name: 'Cases', visible: false},
                'deal': {name: 'Deals', visible: false},
                'email': {name: 'Emails', visible: false}
            };
            scope.history.activeFilter = '';
            scope.history.showMoreText = 'Show more';
            scope.history.loadMore = loadMore;
            scope.history.reloadHistory = reloadHistory;
            scope.history.addNote = addNote;
            scope.history.editNote = editNote;
            scope.history.pinNote = pinNote;
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
                    });
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
                if (noteTargets.indexOf(scope.target) !== -1) {
                    var notePromise;

                    if (scope.target === 'account' && obj.contact && obj.contact.length) {
                        var filterquery = '(content_type:' + scope.target + ' AND object_id:' + obj.id + ')';

                        // Show all notes of contacts linked to the account
                        for (var i = 0; i < obj.contact.length; i++) {
                            filterquery += ' OR (content_type:contact AND object_id:' + obj.contact[i] + ')';
                        }

                        notePromise = NoteDetail.query({filterquery: filterquery, size: requestLength}).$promise;
                    } else {
                        notePromise = NoteDetail.query({filterquery: 'content_type:' + scope.target + ' AND object_id:' + obj.id, size: requestLength }).$promise;
                    }

                    promises.push(notePromise);  // Add promise to list of all promises for later handling

                    notePromise.then(function(results) {
                        results.forEach(function(note) {
                            // Set notes shown property to true to have toggled open
                            // as default.
                            note.shown = true;
                            // If it's a contact's note, add extra attribute to the note
                            // so we can identify it in the template
                            if (scope.target === 'account' && note.content_type === 'contact') {
                                note.showContact = true;
                            }

                            history.push(note);
                        });
                    });
                }

                // Check if we need to fetch cases
                if (caseTargets.indexOf(scope.target) !== -1) {
                    var casePromise = Case.query({filterquery: scope.target + ':' + obj.id, size: 100}).$promise;
                    promises.push(casePromise);  // Add promise to list of all promises for later handling

                    casePromise.then(function(response) {
                        response.objects.forEach(function(caseItem) {
                            caseItem.historyType = 'case';
                            history.push(caseItem);
                            NoteDetail.query({filterquery: 'content_type:case AND object_id:' + caseItem.id, size: 15})
                                .$promise.then(function(notes) {
                                    caseItem.notes = notes;
                                });
                        });
                    });
                }

                // Check if we need to fetch deals
                if (dealTargets.indexOf(scope.target) !== -1) {
                    var dealPromise = DealDetail.query({filterquery: scope.target + ':' + obj.id, size: requestLength}).$promise;
                    promises.push(dealPromise);  // Add promise to list of all promises for later handling

                    dealPromise.then(function(results) {
                        results.forEach(function(deal) {
                            NoteDetail.query({
                                filterquery: 'content_type:deal AND object_id:' + deal.id,
                                size: 5,
                            }).$promise.then(function(notes) {
                                deal.notes = notes;
                            });
                            history.push(deal);
                        });
                    });
                }

                // Check if we need to fetch emails
                if (emailTargets.indexOf(scope.target) !== -1) {
                    var tenantEmailAccountPromise = EmailAccount.query().$promise;
                    promises.push(tenantEmailAccountPromise); // Add tenant email query to promises list

                    var emailPromise;
                    if (scope.target === 'account') {
                        emailPromise = EmailDetail.query({account_related: obj.id, size: requestLength}).$promise;
                    } else {
                        emailPromise = EmailDetail.query({contact_related: obj.id, size: requestLength}).$promise;
                    }
                    promises.push(emailPromise);  // Add promise to list of all promises for later handling

                    $q.all([tenantEmailAccountPromise, emailPromise]).then(function(results) {
                        var tenantEmailAccountList = results[0].results;
                        var emailMessageList = results[1];

                        emailMessageList.forEach(function(email) {
                            tenantEmailAccountList.forEach(function(emailAddress) {
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
                    var orderedHistoryList = {pinned: [], nonPinned: {}, totalItems: history.length};

                    // To properly sort the history list we need to compare dates
                    // because email doesn't have the modified key we decided
                    // to add an extra key called historySortDate which the list
                    // uses to sort properly. We add the sent_date of email to the
                    // object, and the modified date for the other types.
                    for (var i = 0; i < history.length; i++) {
                        if (history[i].historyType === 'email') {
                            history[i].historySortDate = history[i].sent_date;
                        } else {
                            history[i].historySortDate = history[i].modified;
                        }
                    }

                    $filter('orderBy')(history, 'historySortDate', true).forEach(function(item) {
                        var date = '';
                        var key = '';

                        if (item.is_pinned) {
                            orderedHistoryList.pinned.push(item);
                        } else {
                            if (item.hasOwnProperty('modified')) {
                                date = item.modified;
                            } else {
                                date = item.sent_date;
                            }

                            key = moment(date).year() + '-' + (moment(date).month() + 1);

                            if (!orderedHistoryList.nonPinned.hasOwnProperty(key)) {
                                orderedHistoryList.nonPinned[key] = [];
                            }

                            orderedHistoryList.nonPinned[key].push(item);
                        }
                    });

                    scope.history.list = orderedHistoryList;
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
                        object_id: scope.object.id,
                    }),
                }).success(function() {
                    $state.go($state.current, {}, {reload: true});
                });
            }

            function editNote(note) {
                var modalInstance = $uibModal.open({
                    templateUrl: 'utils/controllers/note_edit.html',
                    controller: 'EditNoteModalController',
                    size: 'lg',
                    resolve: {
                        note: function() {
                            return note;
                        },
                    },
                });

                modalInstance.result.then(function() {
                    $state.go($state.current, {}, {reload: true});
                });
            }

            function pinNote(note, isPinned) {
                Note.update({id: note.id}, {is_pinned: isPinned}, function() {
                    $state.go($state.current, {}, {reload: true});
                });
            }

            function deleteNote(note) {
                var month = moment(note.modified).format('M');
                var year = moment(note.modified).format('YYYY');
                var index;

                if (confirm('Are you sure?')) {
                    Note.delete({
                        id: note.id,
                    }, function() {  // On success
                        if (note.is_pinned) {
                            index = scope.history.list.pinned.indexOf(note);
                            scope.history.list.pinned.splice(index, 1);
                        } else {
                            index = scope.history.list.nonPinned[year + '-' + month].indexOf(note);
                            scope.history.list.nonPinned[year + '-' + month].splice(index, 1);
                        }
                    }, function(error) {  // On error
                        alert('something went wrong.');
                    });
                }
            }
        },
    };
}
