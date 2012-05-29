from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models.loading import get_model
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext, ugettext_lazy as _
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from attachments.models import Attachment
from attachments.forms import AttachmentForm, AttachmentDisplayNameForm

def add_url_for_obj(obj):
    return reverse('add_attachment', kwargs={
                        'app_label': obj._meta.app_label,
                        'module_name': obj._meta.module_name,
                        'pk': obj.pk
                    })

@require_POST
@login_required
def add_attachment(request, app_label, module_name, pk,
                   template_name='attachments/add.html', extra_context={}):

    next = request.POST.get('next', '/')
    model = get_model(app_label, module_name)
    if model is None:
        return HttpResponseRedirect(next)
    obj = get_object_or_404(model, pk=pk)
    form = AttachmentDisplayNameForm(request.POST, request.FILES)
    if form.is_valid():
        att = form.save(request, obj)
        #messages.add_message(request, messages.SUCCESS, 'Your attachement was uploaded.')
        return HttpResponse(att.id, content_type="application/json")
    else:
        template_context = {
            'form': form,
            'form_url': add_url_for_obj(obj),
            'next': next,
        }
        template_context.update(extra_context)
        return render_to_response(template_name, template_context,
                                  RequestContext(request))

@require_POST
@login_required
def delete_attachment(request, attachment_pk):
    g = get_object_or_404(Attachment, pk=attachment_pk)
    if request.user.has_perm('delete_foreign_attachments') \
       or request.user == g.creator:
        g.delete()
        messages.add_message(request, messages.SUCCESS, 'Your attachment was deleted.')
    next = request.POST.get('next') or '/'
    return HttpResponseRedirect(next)

def retrieve_attachment(request, attachment_pk, text_as_plain=True, safe=False):
    
    attachment = get_object_or_404(Attachment, pk=attachment_pk)
    # In the next line, we read a whole file into memory. It may be better to use file.chunks()
    # instead of file.read(), but according to a django-users post -- see
    # http://groups.google.com/group/django-users/browse_thread/thread/9837fc79c0528db1/647ff82eff26d0b1?lnk=gst&q=chunks#647ff82eff26d0b1
    # -- that might trigger subtle bugs.
    safe = safe or attachment.safe
    mimetype = attachment.mime_type

    if mimetype and mimetype.startswith('text/'):
        if text_as_plain and not safe:
            mimetype = 'text/plain';

    file = attachment.attachment_file             
    response = HttpResponse(file.read(), mimetype=mimetype)
    
    if not (mimetype=='text/plain' or safe):
        response['Content-Disposition'] = 'attachment; filename='+attachment.filename

    # Response.__init__, when not given mimetype, uses the default. We don't want that.
    if not mimetype:
        del response['Content-Type']
            
    return response
