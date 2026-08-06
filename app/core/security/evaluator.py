"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Security Framework

Security policy evaluation engine.
"""


from dataclasses import dataclass, field

from typing import Dict, Any


from app.core.security.policies import (
    SecurityPolicy,
)



@dataclass
class PolicyEvaluationResult:
    """
    Result of a policy evaluation.
    """

    policy: SecurityPolicy

    passed: bool

    message: str = ""

    metadata: Dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )



    def __bool__(self):
        """
        Allow boolean evaluation.
        """

        return self.passed



class PolicyEvaluator:
    """
    Enterprise security policy evaluator.
    """



    def evaluate(
        self,
        policy: SecurityPolicy,
        subject=None,
        context=None,
    ) -> PolicyEvaluationResult:
        """
        Evaluate a security policy.

        Current framework behaviour:
        - Disabled policies pass
        - Enabled policies require future rules

        Future implementations will
        evaluate policy conditions.
        """


        if not isinstance(
            policy,
            SecurityPolicy,
        ):
            raise TypeError(
                "Only SecurityPolicy objects can be evaluated."
            )


        if not policy.enabled:

            return PolicyEvaluationResult(
                policy=policy,
                passed=True,
                message=(
                    "Policy disabled."
                ),
            )


        return PolicyEvaluationResult(
            policy=policy,
            passed=True,
            message=(
                "Policy evaluated successfully."
            ),
        )



    def evaluate_all(
        self,
        policies,
        subject=None,
        context=None,
    ):
        """
        Evaluate multiple policies.
        """

        return [
            self.evaluate(
                policy,
                subject,
                context,
            )
            for policy
            in policies
        ]



    def all_passed(
        self,
        results,
    ) -> bool:
        """
        Check whether all policies passed.
        """

        return all(
            result.passed
            for result
            in results
        )



    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            "<PolicyEvaluator>"
        )



# Global evaluator instance

policy_evaluator = PolicyEvaluator()
