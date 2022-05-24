from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import TopicForm, EntryForm
from .models import Topic, Entry


def index(request):
    return render(request, 'learning_logs/index.html')


@login_required
def topics(request):
    """
    Shows the list of topics
    """
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)


@login_required
def topic(request, topic_id):
    """
    Shows one topic and all it's notes
    """
    topic = Topic.objects.get(id=topic_id)
    if topic.owner != request.user:
        raise Http404

    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)


@login_required
def new_topic(request):
    """
    Defines a new topic
    """
    if request.method != 'POST':
        # There is no data; create an empty form
        form = TopicForm()
    else:
        # There is a POST data; process data
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')

    # Show empty or invalid form
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    """
    Add a new note to the Topic
    """
    topic = Topic.objects.get(id=topic_id)
    if request.method != 'POST':
        # creation of new empty form.
        form = EntryForm()
    else:
        # Send the data, process the data.
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)

    # Show empty or invalid form
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    """
    Edit the entry
    """
    entry = Entry.objects.get(id=entry_id)
    entry.last_edition = timezone.now()
    topic = entry.topic
    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        # The original request; the form is filled with the data of the current record.
        form = EntryForm(instance=entry)
    else:
        # Send the data, process the data.
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)
    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)
