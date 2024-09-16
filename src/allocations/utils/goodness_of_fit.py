from django.db.models import Count
from classes.models import RequirementSkill, Competency
from users.models import Demonstrator, UserAvailability
from allocations.models import Allocation
from allocations.utils.constraint_manager import HardConstraintManager, PrimaryConstraintManager, SecondaryConstraintManager
from allocations.utils.constraint_filter import ConstrantFilterQuery as cf

class GoodnessOfFit:
    """The `GoodnessOfFit` class provides various static methods to evaluate and generate reports on the goodness of fit 
    for the allocation system. This includes calculating ratios, compliance with constraints, skill match scores, 
    utilization rates, and statistical measures like chi-square for load balancing.

    This class interacts with several models including `Allocation`, `RequirementSkill`, `Competency`, `Demonstrator`, 
    and `UserAvailability` to gather and analyze data for generating metrics and reports.

    :param allocation: An instance of the `Allocation` model representing the current allocation being processed.
    :type allocation: `Allocation`
    """
    
    @staticmethod
    def get_total_allocation():
        """Get the total number of allocations.

        :return: The total number of allocations.
        :rtype: int
        """
        return Allocation.objects.all().count()
    
    @staticmethod
    def get_total_allocation_notnull():
        """Get the total number of allocations that have a demonstrator assigned.

        :return: The total number of allocations with a non-null demonstrator.
        :rtype: int
        """
        return Allocation.objects.filter(demonstrator__isnull=False).count()
        
    @staticmethod
    def get_distribution_required_skills():
        """Get the distribution of required skills across all sessions.

        :return: A dictionary where the keys are skill names and the values are their respective counts.
        :rtype: dict
        """
        skill_distribution = RequirementSkill.objects.values('skill__name').annotate(count=Count('skill')).order_by('-count')
        skill_dict = {}
        for skill in skill_distribution:
            skill_dict[skill['skill__name']] = skill['count']
        
        return skill_dict
    
    @staticmethod
    def get_distribution_competencies():
        """Get the distribution of competencies across all demonstrators.

        :return: A dictionary where the keys are skill names and the values are their respective counts.
        :rtype: dict
        """
        skill_distribution = Competency.objects.values('skill__name').annotate(count=Count('skill')).order_by('-count')
        skill_dict = {}
        for skill in skill_distribution:
            skill_dict[skill['skill__name']] = skill['count']
        return skill_dict
    
    @staticmethod
    def get_ratio_hard_constraint():
        """Calculate the ratio of valid demonstrators for allocations based on hard constraints.

        :return: The ratio of valid demonstrators to total allocations.
        :rtype: float
        """
        valid_count = 0
        all_demonstrators = list(Demonstrator.objects.all())
        all_allocation= list(Allocation.objects.filter(demonstrator__isnull=False))
        for allocation in all_allocation:
            valid_demonstrator = [dem for dem in all_demonstrators if
                                  HardConstraintManager.is_demonstrator_not_double_booked(allocation, dem) and
                                  HardConstraintManager.is_demonstator_available_for_all(allocation, dem)
                                  ]
            valid_count += len(valid_demonstrator)
        total_allocations = len(all_allocation)
        return valid_count/total_allocations
    
    @staticmethod
    def get_ratio_primary_constraint():
        """Calculate the ratio of valid demonstrators for allocations based on primary constraints.

        :return: The ratio of valid demonstrators to total allocations.
        :rtype: float
        """
        valid_count = 0
        all_demonstrators = list(Demonstrator.objects.all())
        all_allocation= list(Allocation.objects.filter(demonstrator__isnull=False))
        for allocation in all_allocation:
            valid_demonstrator = [dem for dem in all_demonstrators if
                                  PrimaryConstraintManager.demonstrator_has_beginner_skill(allocation, dem)
                                  ]
            valid_count += len(valid_demonstrator)
        total_allocations = len(all_allocation)
        return valid_count/total_allocations
    
    @staticmethod
    def get_ratio_secondary_constraint():
        """Calculate the ratio of valid demonstrators for allocations based on secondary constraints.

        :return: The ratio of valid demonstrators to total allocations.
        :rtype: float
        """
        valid_count = 0
        all_demonstrators = list(Demonstrator.objects.all())
        all_allocation= list(Allocation.objects.filter(demonstrator__isnull=False))
        for allocation in all_allocation:
            valid_demonstrator = [dem for dem in all_demonstrators if
                                  SecondaryConstraintManager.demonstrator_has_skill_or_higher(allocation, dem)
                                  ]
            valid_count += len(valid_demonstrator)
        total_allocations = len(all_allocation)
        return valid_count/total_allocations
    
    @staticmethod
    def get_distribution_tertiary_constraint():
        """(Placeholder) Calculate the distribution based on tertiary constraints.

        :return: Not implemented.
        :rtype: None
        """
        pass
    
    @staticmethod
    def get_percentage_allocated():
        """Calculate the percentage of allocations that have been approved.

        :return: The percentage of approved allocations.
        :rtype: float
        """
        total_approved = Allocation.objects.filter(approved=True).count()
        
        return total_approved/GoodnessOfFit.get_total_allocation()
    
    @staticmethod
    def get_hard_constraint_compliance():
        """Calculate the compliance percentage for hard constraints across all allocations.

        :return: The percentage of allocations that pass hard constraints.
        :rtype: float
        """
        total_pass = len(cf.filter_allocations_by_hard_constraints_post_approve(Allocation.objects.all()))
        return total_pass/GoodnessOfFit.get_total_allocation_notnull()
        
    
    @staticmethod
    def get_primary_constraint_compliance():
        """Calculate the compliance percentage for primary constraints across all allocations.

        :return: The percentage of allocations that pass primary constraints.
        :rtype: float
        """
        total_pass = len(cf.filter_allocation_by_primary_soft_constraints(Allocation.objects.all()))
        return total_pass/GoodnessOfFit.get_total_allocation_notnull()
    
    @staticmethod
    def get_secondary_constraint_compliance():
        """Calculate the compliance percentage for secondary constraints across all allocations.

        :return: The percentage of allocations that pass secondary constraints.
        :rtype: float
        """
        total_pass = len(cf.filter_allocation_by_secondary_soft_constraints(Allocation.objects.all()))
        return total_pass/GoodnessOfFit.get_total_allocation_notnull()
    
    @staticmethod
    def get_tertiary_constraint_compliance():
        """(Placeholder) Calculate the compliance percentage for tertiary constraints.

        :return: Not implemented.
        :rtype: None
        """
        pass
    
    @staticmethod
    def get_skill_match_score_single(allocation):
        """Calculate the skill match score for a single allocation.

        :param allocation: The allocation to calculate the skill match score for.
        :type allocation: `Allocation`
        :return: The skill match score for the allocation.
        :rtype: float
        """
        required_skills = RequirementSkill.objects.filter(class_session=allocation.class_session)
        demonstrator_competencies = Competency.objects.filter(demonstrator=allocation.demonstrator)
        competency_dict = {comp.skill.name: comp.skill.level for comp in demonstrator_competencies}
        
        total_score = 0
        max_score = 0
        for required_skill in required_skills:
            skill_name = required_skill.skill.name
            skill_level = required_skill.skill.level
            max_score += 1
            
            if skill_name in competency_dict:
                if competency_dict[skill_name] >= skill_level:
                    total_score += 1
                else:
                    total_score += (competency_dict[skill_name] / skill_level)
        
        return total_score / max_score if max_score > 0 else 0
    
    @staticmethod
    def get_skill_match_score_distribution():
        """Calculate the average skill match score across all allocations.

        :return: The average skill match score.
        :rtype: float
        """
        allocations = Allocation.objects.filter(demonstrator__isnull=False)
        total_skill_match_score = 0
        for allocation in allocations:
            total_skill_match_score += GoodnessOfFit.get_skill_match_score_single(allocation)
        
        average_skill_match_score = total_skill_match_score / allocations.count() if allocations.count() > 0 else 0
        
        return average_skill_match_score
    
    @staticmethod
    def get_utilisation_rate():
        """Calculate the utilisation rate of demonstrators.

        :return: The utilisation rate of demonstrators.
        :rtype: float
        """
        total_used = Allocation.objects.filter(demonstrator__isnull = False).values('demonstrator').distinct().count()
        total_demonstrator  = Demonstrator.objects.all().distinct().count()
        return total_used/total_demonstrator
    
    @staticmethod
    def get_preference_fulfillment():
        """(Placeholder) Calculate the fulfillment of demonstrator preferences.

        :return: Not implemented.
        :rtype: None
        """
        pass
    
    @staticmethod
    def get_demonstrator_time_load_balance_chi_square():
        """Calculate the chi-square statistic for demonstrator time load balance.

        :return: The chi-square statistic for time load balance.
        :rtype: float
        """
        demonstrators = Demonstrator.objects.all()
        total_allocations = GoodnessOfFit.get_total_allocation_notnull()
        total_availability = 0
        demonstrator_availabilities = []
        for dem in demonstrators:
            available_timeslots = UserAvailability.objects.filter(user=dem.user, is_available=True).count()
            demonstrator_availabilities.append(available_timeslots)
            total_availability += available_timeslots
        
        expected_allocations = [total_allocations * (availability / total_availability) for availability in demonstrator_availabilities]
        
        observed_allocations = [Allocation.objects.filter(demonstrator=dem).count() for dem in demonstrators]
        
        chi_square_stat = sum((observed - expected) ** 2 / expected if expected != 0 else 0 
                              for observed, expected in zip(observed_allocations, expected_allocations))
    
        return chi_square_stat
    
    @staticmethod
    def normalise_chi_square_stat(chi_square_stat, max_chi_square = 2700):
        """Normalize the chi-square statistic to a score between 0 and 1.

        :param chi_square_stat: The chi-square statistic to normalize.
        :type chi_square_stat: float
        :param max_chi_square: The maximum chi-square value used for normalization, defaults to 1000.
        :type max_chi_square: int, optional
        :return: The normalized chi-square score.
        :rtype: float
        """
        normalized_score = 1 - min(chi_square_stat / max_chi_square, 1)
        return normalized_score
        
    @staticmethod
    def normalise_weights(weights):
        """Normalize a list of weights to sum to 1.

        :param weights: The list of weights to normalize.
        :type weights: list
        :return: The normalized list of weights.
        :rtype: list
        """
        total = sum(weights)
        normalised_weights = [weight/total for weight in weights]
        return normalised_weights
    
    
    @staticmethod
    def calculate_overall_fit(scores):
        """Calculate the overall fit score based on a set of individual scores.

        :param scores: A list of individual scores.
        :type scores: list
        :return: A tuple containing the unweighted score and the weighted score.
        :rtype: tuple (float, float)
        """
        hard_compliance_weight = 100
        primary_compliance_weight = 10
        secondary_compliance_weight = 7
        skill_distribution_weight = 20
        utilisation_rate_weight = 5
        time_distribution_weight = 2
        
        weights = [hard_compliance_weight,
                   primary_compliance_weight, 
                   secondary_compliance_weight,
                   skill_distribution_weight,
                   utilisation_rate_weight,
                   time_distribution_weight]
        
        normalised_weights = GoodnessOfFit.normalise_weights(weights)
        
        unweighted_score = sum(scores)/len(scores)
        weighted_score = sum( weight * score for weight, score in zip(normalised_weights, scores))
        
        return unweighted_score, weighted_score
    
    @staticmethod
    def convert_seconds_to_hms(seconds):
        """Convert a time duration from seconds to hours, minutes, and seconds.

        :param seconds: The time duration in seconds.
        :type seconds: int
        :return: A tuple containing hours, minutes, and seconds.
        :rtype: tuple (int, int, int)
        """
        hours = seconds // 3600
        remaining_seconds = seconds % 3600
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        return hours, minutes, seconds
    
    @staticmethod
    def generate_report(elapsed_time=0):
        """Generate a comprehensive report on the goodness of fit, including various metrics and their compliance scores.

        :param elapsed_time: The time taken for the allocation process, in seconds. Defaults to 0 if time isn't provided
        :type elapsed_time: int
        :return: A tuple containing the report string and a dictionary of results.
        :rtype: tuple (str, dict)
        """
        
        #Collect data
        no_error_message = "No Error Encountered"
        e1 = no_error_message
        e2 = no_error_message
        e3 = no_error_message
        e4 = no_error_message
        e5 = no_error_message
        e6 = no_error_message
        e7 = no_error_message
        
        try:
            total_allocations = GoodnessOfFit.get_total_allocation()
            total_allocations_not_null = GoodnessOfFit.get_total_allocation_notnull()
            print(f"Total allocations {total_allocations}. Not Null {total_allocations_not_null}")
        except Exception as e:
            print(e)
            e1 = e
            total_allocations = "Error"
            total_allocations_not_null = "Error"
        try:
            hard_compliance_score = GoodnessOfFit.get_hard_constraint_compliance()
            primary_compliance_score = GoodnessOfFit.get_primary_constraint_compliance()
            secondary_compliance_score = GoodnessOfFit.get_secondary_constraint_compliance()
            print(f"Compliance Scores. Hard {hard_compliance_score}, Primary {primary_compliance_score}, Secondary {secondary_compliance_score}")
        except Exception as e:
            print(e)
            e2 = e
            hard_compliance_score = "Error"
            primary_compliance_score = "Error"
            secondary_compliance_score = "Error"
        try:    
            skill_match_score = GoodnessOfFit.get_skill_match_score_distribution()
            print(f"Skill Match: {skill_match_score}")
        except Exception as e:
            print(e)
            e3 = e
            skill_match_score = "Error"
        try:
            utilization_rate = GoodnessOfFit.get_utilisation_rate()
            print(f"Utilisation rate {utilization_rate}")
        except Exception as e:
            print(e)
            e4 = e
            utilization_rate = "Error"
        try:
            chi_square_stat = GoodnessOfFit.get_demonstrator_time_load_balance_chi_square()
            normalized_chi_square = GoodnessOfFit.normalise_chi_square_stat(chi_square_stat)
            print(f"Chi Square Statistic {chi_square_stat}. Normalised {normalized_chi_square}")
        except Exception as e:
            print(e)
            e5 = e
            chi_square_stat = "Error"
            normalized_chi_square = "Error"
        try:
            scores = [hard_compliance_score,
                      primary_compliance_score,
                      secondary_compliance_score,
                      skill_match_score,
                      utilization_rate,
                      normalized_chi_square]
            unweighted_score, weighted_score = GoodnessOfFit.calculate_overall_fit(scores)
            print(f"Overall Scores - Weighted{weighted_score}, Unweighted {unweighted_score}")
        except Exception as e:
            print(e)
            e6 = e
            unweighted_score = "Error"
            weighted_score = "Error"
        
        try:
            #Fix Later
            #hard_ratio = GoodnessOfFit.get_ratio_hard_constraint()
            #primary_ratio = GoodnessOfFit.get_ratio_primary_constraint()
            #secondary_ratio = GoodnessOfFit.get_ratio_secondary_constraint()
            print(f"Constraint Ratio - Hard {hard_ratio}, Primary {primary_ratio}, Secondary {secondary_ratio}")
        except Exception as e:
            print(e)
            e7 = e
            hard_ratio = "Error"
            primary_ratio = "Error"
            secondary_ratio = "Error"
        
        
        results_dict = {
            "total_allocations": total_allocations,
            "total_allocations_not_null": total_allocations_not_null,
            "hard_ratio": hard_ratio,
            "primary_ratio": primary_ratio,
            "secondary_ratio": secondary_ratio, 
            "hard_compliance_score": hard_compliance_score,
            "primary_compliance_score": primary_compliance_score,
            "secondary_compliance_score":  secondary_compliance_score,
            "skill_match_score" : skill_match_score,
            "utilization_rate" : utilization_rate,
            "chi_square_stat" : chi_square_stat,
            "normalized_chi_square" : normalized_chi_square,
            "unweighted_score" : unweighted_score, 
            "weighted_score" : weighted_score
        }
        
        hour, min, sec = GoodnessOfFit.convert_seconds_to_hms(elapsed_time) 
        #Report
        report = f"""
        # Allocation System Goodness of Fit Report
    **Key Findings:**
    - **Total Allocations:** {total_allocations}
    - **Total Approved Allocations:** {total_allocations_not_null}
    - **Overall Weighted Score:** {weighted_score}
    - **Hard Constraint Compliance:** {hard_compliance_score}
    - **Total Time Taken for Allocation:** {hour}hr:{min}min:{sec}sec
    
    **Detailed Findings**
    ## Detailed Results
    ### Overall Fit Scores
    - **Unweighted Score:** {unweighted_score}
    - **Weighted Score:** {weighted_score}
    
    ### Valid Demonstrators : Allocation Ratio
    - **Hard Constraints** {hard_ratio}
    - **Primary Constraints** {primary_ratio}
    - **Secondary Constraints** {secondary_ratio}

    ### Constraint Compliance
    - **Hard Constraints:** {hard_compliance_score}
    - **Primary Soft Constraints:** {primary_compliance_score}
    - **Secondary Soft Constraints:** {secondary_compliance_score}

    ### Skill Match Quality
    - **Average Skill Match Score:** {skill_match_score}

    ### Demonstrator Utilization Rate
    - **Utilization Rate:** {utilization_rate}

    ### Time Load Balance (Chi-Square Test)
    - **Chi-Square Statistic:** {chi_square_stat}
    - **Normalized Score:** {normalized_chi_square}
        
        ### Error Messages
        - Total allocation {e1}
        - Compliance score {e2}
        - Skill Match score {e3}
        - Utilisation rate {e4}
        - Chi square Test {e5}
        - Overall Fit {e6}
        - Constraint Ratio {e7}
        """
        
        return report, results_dict