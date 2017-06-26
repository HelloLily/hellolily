angular.module('app.utils.directives').directive('activityStream', ActivityStreamDirective);

ActivityStreamDirective.$inject = ['$filter', '$q', '$state', 'Case', 'Deal', 'EmailAccount', 'EmailDetail', 'HLGravatar',
    'HLResource', 'HLUtils', 'HLForms', 'Note', 'NoteDetail', 'User'];
function ActivityStreamDirective($filter, $q, $state, Case, Deal, EmailAccount, EmailDetail, HLGravatar,
    HLResource, HLUtils, HLForms, Note, NoteDetail, User) {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            target: '=',
            object: '=',
            dateStart: '=?',
            dateEnd: '=?',
            extraObject: '=?',
            parentObject: '=?',
        },
        templateUrl: 'utils/directives/activity_stream.html',
        link: function(scope, element, attrs) {
            var page = 0;
            var pageSize = 50;

            scope.activity = {};
            scope.activity.list = [];
            scope.activity.types = {
                '': {name: 'All', visible: true},
                'note': {name: 'Notes', visible: false},
                'case': {name: 'Cases', visible: false},
                'deal': {name: 'Deals', visible: false},
                'email': {name: 'Emails', visible: false},
            };
            scope.activity.activeFilter = '';
            scope.activity.showMoreText = 'Show more';
            scope.activity.loadMore = loadMore;
            scope.activity.reloadactivity = reloadactivity;
            scope.activity.addNote = addNote;
            scope.activity.pinNote = pinNote;
            scope.activity.removeFromList = removeFromList;
            scope.activity.filterType = filterType;

            scope.note = {};
            scope.note.type = 0;

            activate();

            ////////

            function activate() {
                HLUtils.blockUI('#activityStreamBlockTarget', true);
                // Somehow calling autosize on page content load does not work
                // in the activity stream.
                autosize($('textarea'));
                loadMore();
            }

            function filterType(value) {
                var key;
                var selectedCount;

                scope.activity.activeFilter = value;
                // Loop through the months to hide the monthname when there
                // aren't any items in that month that are shown due to
                // the filter that is being selected.
                for (key in scope.activity.list.nonPinned) {
                    selectedCount = $filter('filter')(scope.activity.list.nonPinned[key].items, {activityType: value}).length;
                    scope.activity.list.nonPinned[key].isVisible = !!selectedCount;
                }
            }

            function loadMore() {
                if (!scope.object.$resolved) {
                    scope.object.$promise.then(function(obj) {
                        _fetchactivity(obj);
                    });
                } else {
                    _fetchactivity(scope.object);
                }
            }

            function reloadactivity() {
                page -= 1;
                loadMore();
            }

            function _fetchactivity(obj) {
                var activity = [];
                var promises = [];
                var neededLength = (page + 1) * pageSize;
                var requestLength = neededLength + 1;
                var notePromise;
                var dateQuery = '';
                var emailDateQuery = '';
                var casePromise;
                var dealPromise;
                var tenantEmailAccountPromise;
                var emailPromise;
                var i;
                var filterquery;
                var currentObject = obj;
                var contentType = scope.target;

                if (scope.dateStart && scope.dateEnd) {
                    dateQuery = ' AND modified:[' + scope.dateStart + ' TO ' + scope.dateEnd + ']';
                    emailDateQuery = 'sent_date:[' + scope.dateStart + ' TO ' + scope.dateEnd + ']';
                }

                page += 1;

                filterquery = '(content_type:' + contentType + ' AND object_id:' + currentObject.id + ')';

                if (contentType === 'account' && currentObject.contacts) {
                    // Show all notes of contacts linked to the account.
                    for (i = 0; i < currentObject.contacts.length; i++) {
                        filterquery += ' OR (content_type:contact AND object_id:' + currentObject.contacts[i].id + ')';
                    }
                }

                if (scope.extraObject) {
                    filterquery += ' OR (content_type:' + scope.extraObject.target + ' AND object_id:' + scope.extraObject.object.id + dateQuery + ')';
                }

                filterquery = '(' + filterquery + ')';

                notePromise = NoteDetail.query({filterquery: filterquery, size: requestLength}).$promise;

                promises.push(notePromise);  // Add promise to list of all promises for later handling

                notePromise.then(function(results) {
                    results.forEach(function(note) {
                        // Get user for notes to show profile picture correctly.
                        User.get({id: note.author.id, is_active: 'All'}, function(userObject) {
                            note.author = userObject;
                        });

                        // If it's a contact's note, add extra attribute to the note
                        // so we can identify it in the template.
                        if (scope.target === 'account' && note.content_type === 'contact') {
                            note.showContact = true;
                        }

                        activity.push(note);
                    });
                });

                if (scope.extraObject) {
                    currentObject = scope.extraObject.object;
                    contentType = scope.extraObject.target;
                }

                // We don't have to fetch extra objects for the case or deal
                // activity list. So continue if we have an extra object or if
                // we're dealing with something else than a case or deal.
                if (contentType !== 'case' && contentType !== 'deal') {
                    filterquery = contentType + '.id:' + currentObject.id;

                    casePromise = Case.search({filterquery: filterquery + dateQuery, size: 100}).$promise;

                    promises.push(casePromise);  // Add promise to list of all promises for later handling

                    casePromise.then(function(response) {
                        response.objects.forEach(function(caseItem) {
                            // Get user object for the assigned to user.
                            if (caseItem.assigned_to) {
                                User.get({id: caseItem.assigned_to.id, is_active: 'All'}, function(userObject) {
                                    caseItem.assigned_to = userObject;
                                });
                            }

                            if (caseItem.created_by) {
                                // Get user object for the created by user.
                                User.get({id: caseItem.created_by.id, is_active: 'All'}, function(userObject) {
                                    caseItem.created_by = userObject;
                                });
                            }

                            caseItem.activityType = 'case';

                            activity.push(caseItem);
                            NoteDetail.query({filterquery: 'content_type:case AND object_id:' + caseItem.id, size: 15})
                                .$promise.then(function(notes) {
                                    angular.forEach(notes, function(note) {
                                        // Get user for notes to show profile picture correctly.
                                        User.get({id: note.author.id, is_active: 'All'}, function(author) {
                                            note.author = author;
                                        });
                                    });

                                    caseItem.notes = notes;
                                });
                        });
                    });

                    dealPromise = Deal.search({filterquery: filterquery + dateQuery, size: requestLength}).$promise;
                    promises.push(dealPromise);  // Add promise to list of all promises for later handling

                    dealPromise.then(function(results) {
                        results.objects.forEach(function(deal) {
                            if (deal.assigned_to) {
                                // Get user object for the assigned to user.
                                User.get({id: deal.assigned_to.id, is_active: 'All'}, function(userObject) {
                                    deal.assigned_to = userObject;
                                });
                            }

                            if (deal.created_by) {
                                // Get user object to show profile picture correctly.
                                User.get({id: deal.created_by.id, is_active: 'All'}, function(userObject) {
                                    deal.created_by = userObject;
                                });
                            }

                            NoteDetail.query({
                                filterquery: 'content_type:deal AND object_id:' + deal.id,
                                size: 5,
                            }).$promise.then(function(notes) {
                                angular.forEach(notes, function(note) {
                                    // Get user for notes to show profile picture correctly.
                                    User.get({id: note.author.id, is_active: 'All'}, function(author) {
                                        note.author = author;
                                    });
                                });

                                deal.notes = notes;
                            });

                            activity.push(deal);
                        });
                    });

                    tenantEmailAccountPromise = EmailAccount.query().$promise;
                    promises.push(tenantEmailAccountPromise);

                    if (contentType === 'account') {
                        emailPromise = EmailDetail.search({account_related: currentObject.id, filterquery: emailDateQuery, size: requestLength}).$promise;
                    } else {
                        emailPromise = EmailDetail.search({contact_related: currentObject.id, filterquery: emailDateQuery, size: requestLength}).$promise;
                    }

                    promises.push(emailPromise);

                    $q.all([tenantEmailAccountPromise, emailPromise]).then(function(results) {
                        var tenantEmailAccountList = results[0].results;
                        var emailMessageList = results[1];

                        emailMessageList.forEach(function(email) {
                            User.search({filterquery: 'email:' + email.sender_email, is_active: 'All'}).$promise.then(function(userResults) {
                                if (userResults.objects[0]) {
                                    email.profile_picture = userResults.objects[0].profile_picture;
                                } else {
                                    email.profile_picture = HLGravatar.getGravatar(email.sender_email);
                                }
                            });

                            tenantEmailAccountList.forEach(function(emailAddress) {
                                if (emailAddress.email_address === email.sender_email) {
                                    email.right = true;
                                }
                            });

                            activity.push(email);
                        });
                    });
                }

                // Get all activity types and add them to a common activity stream.
                $q.all(promises).then(function() {
                    var orderedActivityStream = {pinned: [], nonPinned: {}, totalItems: activity.length};

                    // To properly sort the activity list we need to compare dates
                    // because email doesn't have the modified key we decided
                    // to add an extra key called activitySortDate which the list
                    // uses to sort properly. We add the sent_date of email to the
                    // object, and the modified date for the other types.
                    for (i = 0; i < activity.length; i++) {
                        if (activity[i].activityType === 'email') {
                            activity[i].activitySortDate = activity[i].sent_date;
                        } else if (activity[i].activityType === 'note') {
                            // We want to sort notes on created date.
                            activity[i].activitySortDate = activity[i].date;
                        } else {
                            activity[i].activitySortDate = activity[i].modified;
                        }
                    }

                    $filter('orderBy')(activity, 'activitySortDate', true).forEach(function(item) {
                        var date = '';
                        var key = '';
                        var parentObjectId = scope.parentObject ? scope.parentObject.id : null;

                        scope.activity.types[item.activityType].visible = true;

                        if (item.is_pinned) {
                            orderedActivityStream.pinned.push(item);
                        } else {
                            // Exclude the current item from the activity list.
                            if (item.id !== scope.object.id && item.id !== parentObjectId) {
                                if (item.hasOwnProperty('modified')) {
                                    date = item.modified;
                                } else {
                                    date = item.sent_date;
                                }

                                key = moment(date).year() + '-' + (moment(date).month() + 1);

                                if (!orderedActivityStream.nonPinned.hasOwnProperty(key)) {
                                    orderedActivityStream.nonPinned[key] = {isVisible: true, items: []};
                                }

                                item.shown = true;

                                orderedActivityStream.nonPinned[key].items.push(item);
                            } else {
                                orderedActivityStream.totalItems -= 1;
                            }
                        }
                    });

                    scope.activity.list = orderedActivityStream;

                    HLUtils.unblockUI('#activityStreamBlockTarget');
                });
            }

            function addNote(note, form) {
                note.content_type = scope.object.content_type.id;
                note.object_id = scope.object.id;

                Note.save(note, function() {
                    // Success.
                    scope.note.content = '';
                    toastr.success('I\'ve created the note for you!', 'Done');
                    reloadactivity();
                }, function(response) {
                    // Error.
                    HLForms.setErrors(form, response.data);
                    toastr.error('Uh oh, there seems to be a problem', 'Oops!');
                });
            }

            function pinNote(note, isPinned) {
                Note.update({id: note.id}, {is_pinned: isPinned}, function() {
                    $state.go($state.current, {}, {reload: true});
                });
            }

            function removeFromList(item) {
                var month = moment(item.modified).format('M');
                var year = moment(item.modified).format('YYYY');
                var index;

                if (item.is_pinned) {
                    index = scope.activity.list.pinned.indexOf(item);
                    scope.activity.list.pinned.splice(index, 1);
                } else {
                    index = scope.activity.list.nonPinned[year + '-' + month].items.indexOf(item);
                    scope.activity.list.nonPinned[year + '-' + month].items.splice(index, 1);
                }

                // We might be deleting the last object of a certain month.
                // Check if there are still items and hide the block if needed.
                if (!scope.activity.list.nonPinned[year + '-' + month].items.length) {
                    scope.activity.list.nonPinned[year + '-' + month].isVisible = false;
                }

                scope.$apply();
            }
        },
    };
}
