from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from users.models import Demonstrator

# Create your models here.

class Allocation(models.Model):
    """The `Allocation` model represents the assignment of a demonstrator to a specific class session. 
    It includes information about the session, the assigned demonstrator, and whether the allocation 
    has been approved.

    :param demonstrator: A foreign key linking the allocation to a `Demonstrator`. This field can be null.
    :type demonstrator: `Demonstrator`, optional
    :param class_session: A foreign key linking the allocation to a `ModuleSession` from the `classes` app.
    :type class_session: `ModuleSession`
    :param approved: A boolean field indicating whether the allocation has been approved.
    :type approved: bool, optional
    """
    demonstrator = models.ForeignKey(Demonstrator, on_delete=models.SET_NULL, null=True)
    class_session = models.ForeignKey('classes.ModuleSession', on_delete=models.CASCADE)
    approved = models.BooleanField(default = False)
    
    def ensure_not_approved_if_no_demonstrator(self):
        """Ensure that the allocation is not marked as approved if no demonstrator is assigned.

        If the `demonstrator` field is `None`, this method will set `approved` to `False` and save the model instance.

        :return: None
        """
        if self.demonstrator == None:
            self.approved = False
            self.save()

class AllocationDomain(models.Model):
    """The `AllocationDomain` model represents the set of demonstrators that are considered valid for a particular 
    allocation based on various constraint levels. These constraint levels include hard constraints, primary soft 
    constraints, secondary soft constraints, and tertiary soft constraints.

    :param allocation: A foreign key linking the allocation domain to an `Allocation`.
    :type allocation: `Allocation`
    :param hard_constraint_demonstrators: A many-to-many relationship to `Demonstrator` for those who meet the hard constraints.
    :type hard_constraint_demonstrators: ManyToManyField
    :param primary_soft_constraint_demonstrators: A many-to-many relationship to `Demonstrator` for those who meet the primary soft constraints.
    :type primary_soft_constraint_demonstrators: ManyToManyField
    :param secondary_soft_constraint_demonstrators: A many-to-many relationship to `Demonstrator` for those who meet the secondary soft constraints.
    :type secondary_soft_constraint_demonstrators: ManyToManyField
    :param tertiary_soft_constraint_demonstrators: A many-to-many relationship to `Demonstrator` for those who meet the tertiary soft constraints.
    :type tertiary_soft_constraint_demonstrators: ManyToManyField
    """
    allocation = models.ForeignKey(Allocation, on_delete=models.CASCADE)
    hard_constraint_demonstrators = models.ManyToManyField(Demonstrator, related_name='hard_constraint_demonstrators')
    primary_soft_constraint_demonstrators = models.ManyToManyField(Demonstrator, related_name='primary_soft_constraint_demonstrators')
    secondary_soft_constraint_demonstrators = models.ManyToManyField(Demonstrator, related_name='secondary_soft_constraint_demonstrators')
    tertiary_soft_constraint_demonstrators = models.ManyToManyField(Demonstrator, related_name='tertiary_soft_constraint_demonstrators')

    class Meta:
        verbose_name = "Valid Demonstrator"
        verbose_name_plural = "Valid Demonstrators"

@receiver(post_delete, sender = Demonstrator)
def reset_allocation_approved_status(sender, instance, **kwargs):
    """Signal receiver that resets the approval status of allocations when a demonstrator is deleted.

    This function listens for the `post_delete` signal from the `Demonstrator` model and updates any `Allocation` 
    instances that were linked to the deleted `Demonstrator`, setting their `approved` status to `False`.

    :param sender: The model class that sent the signal, in this case, `Demonstrator`.
    :type sender: Model
    :param instance: The actual instance of `Demonstrator` that was deleted.
    :type instance: `Demonstrator`
    :param kwargs: Additional arguments passed to the signal handler.
    :type kwargs: dict
    :return: None
    """
    Allocation.objects.filter(demonstrator = instance).update(approved = False)