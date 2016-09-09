from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse

# from .core.exceptions import MultipleObjectsReturned

from shared.app_settings import view_list
from views_shared import pendingList, InProgressList, configList, CompletedList, TestDetailList
from views_shared import add_pending, remove_pending, remove_history
from ..forms import PendingForm, ConfigForm, TestConfigFormSet, TestDetailForm

from ..models import (Config, TestConfig)
import json
# logging
import logging
logger = logging.getLogger('checker')


def get_index(request):
    if request.method == 'POST':
        delete_id = request.POST.get('_delete', None)
        delete_mac = request.POST.get('_delete_history', None)
        show_detail = request.POST.get('_show_detail', None)
        delete_test = request.POST.get('_delete_test', None)
        if delete_id:
            remove_pending(current_id=delete_id)
            return HttpResponseRedirect(reverse('checker:index'))
        elif delete_mac:
            remove_history(mac=delete_mac)
            return HttpResponseRedirect(reverse('checker:index'))
        elif show_detail:
            test_detail_form = TestDetailForm(request.POST)
            if test_detail_form.is_valid():
                form_values = test_detail_form.cleaned_data
            for key in form_values.keys():
                request.session[key] = form_values[key]
            return HttpResponseRedirect(reverse('checker:index'))
        elif delete_test:
            delete_test_form = TestDetailForm(request.POST)
            if delete_test_form.is_valid():
                form_values = delete_test_form.cleaned_data
            try:
                remove_history(mac=form_values['show_mac'])
            except:
                raise
            return HttpResponseRedirect(reverse('checker:index'))

        else:
            # create a form instance and populate it with data from the request:
            form = PendingForm(request.POST)
            # check whether it's valid:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                form_values = form.cleaned_data
                request.session['add_test'] = add_pending(config_id=form_values['add_config'].id,
                                                          mac_sensor=form_values['add_mac'])
                # redirect to a new URL:
                return HttpResponseRedirect(reverse('checker:index'))

    # if a GET (or any other method) we'll create a blank form
    else:
        show_mac = request.session.get('show_mac', None)
        show_config = request.session.get('show_config', None)
        if show_mac and show_config:
            detail_list = TestDetailList(mac=show_mac,
                                         config=show_config.id).get()
        add_test = request.session.get('add_test', None)
        test_detail_form = TestDetailForm()
        form = PendingForm()

    context = {
        'view_list': view_list,
        'form': form,
        'add_test': add_test,
        'pending_list': pendingList.get(),
        'in_progress_list': InProgressList().get(),
        # 'in_progress_detail': InProgressDetail().get(),
        'completed_list': CompletedList().get(),
    }
    try:
        context['test_detail_form'] = test_detail_form
    except UnboundLocalError:
        pass
    except:
        raise
    try:
        context['detail_list'] = detail_list
    except UnboundLocalError:
        pass
    except:
        raise

    return render(request, 'checker/index.html', context)


def get_configs(request):
    if request.method == 'POST':
        delete_id = request.POST.get('_delete', None)
        if delete_id:
            config_to_delete = get_object_or_404(Config, id=int(delete_id))
            config_to_delete.delete()
    context = {
        'view_list': view_list,
        'config_list': configList.get()
    }
    return render(request, 'checker/config_list.html', context)


def set_config(request, config_id=None):
    if request.method == 'POST':
        if config_id is None:
            raise Http404("Post error, need config_id")

        qs = TestConfig.objects.filter(config_id=config_id)
        last_row = qs.last()
        if last_row:
            initial_data = [
                {'status': qs.last().next_status,
                 'next_status': qs.last().next_status + 1}
            ]
        else:
            initial_data = [
                {'status': 0,
                 'next_status': 1}
            ]
        test_config_form_set = TestConfigFormSet(prefix='test_config',
                                                 data=request.POST,
                                                 initial=initial_data)

        config_instance = get_object_or_404(Config, id=config_id)
        name_form = ConfigForm(request.POST, instance=config_instance)

        if name_form.is_valid() and test_config_form_set.is_valid():
            # do something with the form data here
            name_form.save()
            test_config_instances = test_config_form_set.save(commit=False)
            for f_instance in test_config_instances:
                f_instance.config_id = config_id
                f_instance.save()

            test_config_form_set.save()

            action = request.POST.get('_action', None)
            if action == 'add':
                return HttpResponseRedirect(
                    reverse('checker:config',
                            kwargs={'config_id': config_id}))
            elif action == 'submit':
                return HttpResponseRedirect(reverse('checker:config_list'))
            else:
                # DELETION
                return HttpResponseRedirect(
                    reverse('checker:config',
                            kwargs={'config_id': config_id}))

    # if a GET (or any other method)
    else:
        if config_id:
            found_config = Config.objects.get(id=config_id)
            name_form = ConfigForm(instance=found_config)

            qs = TestConfig.objects.filter(config_id=config_id)
            last_row = qs.last()
            if last_row:
                initial_data = [
                    {'status': qs.last().next_status,
                     'next_status': qs.last().next_status+1}
                ]
            else:
                initial_data = [
                    {'status': 0,
                     'next_status': 1}
                ]
            test_config_form_set = TestConfigFormSet(
                prefix='test_config',
                queryset=qs,
                initial=initial_data,
            )
        else:
            try:
                new_config = Config.objects.get(name="New Test")
            except Config.DoesNotExist:
                new_config = Config(name="New Test")
                new_config.save()
            return HttpResponseRedirect(
                reverse('checker:config',
                        kwargs={'config_id': new_config.id}))

    context = {
        'view_list': view_list,
        'config_id': config_id,
        'name_form': name_form,
        'config_forms': test_config_form_set,
    }
    return render(request, 'checker/config.html', context)
