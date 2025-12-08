"""
Cloud Security Adapter
Simulates security misconfiguration detection, IAM policy validation, and request log analysis
"""

import os
import json
import logging
import boto3
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from botocore.exceptions import ClientError, BotoCoreError


class CloudSecurityAdapter:
    """Adapter for cloud security operations (AWS/LocalStack)"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.access_key = os.getenv("AWS_ACCESS_KEY_ID", "test")
        self.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
        
        # Initialize AWS clients
        self.session = boto3.Session(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )
        
        self.iam_client = None
        self.cloudwatch_client = None
        self.s3_client = None
        
        self._init_clients()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger"""
        logger = logging.getLogger("cloud_security_adapter")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _init_clients(self):
        """Initialize AWS service clients"""
        try:
            # IAM client for policy validation
            self.iam_client = self.session.client(
                'iam',
                endpoint_url=self.endpoint_url
            )
            
            # CloudWatch client for logs
            self.cloudwatch_client = self.session.client(
                'cloudwatch',
                endpoint_url=self.endpoint_url
            )
            
            # S3 client for security checks
            self.s3_client = self.session.client(
                's3',
                endpoint_url=self.endpoint_url
            )
            
            self.logger.info("AWS clients initialized successfully")
        except Exception as e:
            self.logger.warning(f"Failed to initialize some AWS clients: {e}")
    
    def detect_security_misconfig(self, resource_type: str = "all") -> Dict[str, Any]:
        """
        Detect security misconfigurations in cloud resources
        
        Args:
            resource_type: Type of resource to check (s3, iam, ec2, all)
        
        Returns:
            Dict with detected misconfigurations
        """
        self.logger.info(f"Detecting security misconfigurations for: {resource_type}")
        
        misconfigs = []
        
        if resource_type in ["s3", "all"]:
            s3_misconfigs = self._check_s3_misconfigs()
            misconfigs.extend(s3_misconfigs)
        
        if resource_type in ["iam", "all"]:
            iam_misconfigs = self._check_iam_misconfigs()
            misconfigs.extend(iam_misconfigs)
        
        if resource_type in ["ec2", "all"]:
            ec2_misconfigs = self._check_ec2_misconfigs()
            misconfigs.extend(ec2_misconfigs)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "resource_type": resource_type,
            "misconfigurations": misconfigs,
            "total_count": len(misconfigs),
            "severity_breakdown": self._calculate_severity_breakdown(misconfigs)
        }
    
    def _check_s3_misconfigs(self) -> List[Dict[str, Any]]:
        """Check S3 bucket security misconfigurations"""
        misconfigs = []
        
        try:
            # List all buckets
            response = self.s3_client.list_buckets()
            
            for bucket in response.get('Buckets', []):
                bucket_name = bucket['Name']
                
                # Check public access
                try:
                    public_access = self.s3_client.get_public_access_block(Bucket=bucket_name)
                    if not public_access.get('PublicAccessBlockConfiguration', {}).get('BlockPublicAcls', False):
                        misconfigs.append({
                            "resource": f"s3://{bucket_name}",
                            "type": "public_access",
                            "severity": "high",
                            "description": f"Bucket {bucket_name} allows public access",
                            "recommendation": "Enable BlockPublicAcls in bucket policy"
                        })
                except ClientError:
                    # Public access block not configured
                    misconfigs.append({
                        "resource": f"s3://{bucket_name}",
                        "type": "no_public_access_block",
                        "severity": "medium",
                        "description": f"Bucket {bucket_name} has no public access block configured",
                        "recommendation": "Configure public access block settings"
                    })
                
                # Check encryption
                try:
                    encryption = self.s3_client.get_bucket_encryption(Bucket=bucket_name)
                    if not encryption.get('ServerSideEncryptionConfiguration'):
                        misconfigs.append({
                            "resource": f"s3://{bucket_name}",
                            "type": "no_encryption",
                            "severity": "high",
                            "description": f"Bucket {bucket_name} has no encryption configured",
                            "recommendation": "Enable server-side encryption"
                        })
                except ClientError:
                    misconfigs.append({
                        "resource": f"s3://{bucket_name}",
                        "type": "no_encryption",
                        "severity": "high",
                        "description": f"Bucket {bucket_name} has no encryption configured",
                        "recommendation": "Enable server-side encryption"
                    })
        
        except Exception as e:
            self.logger.error(f"Error checking S3 misconfigs: {e}")
        
        return misconfigs
    
    def _check_iam_misconfigs(self) -> List[Dict[str, Any]]:
        """Check IAM policy misconfigurations"""
        misconfigs = []
        
        try:
            # List all users
            users = self.iam_client.list_users()
            
            for user in users.get('Users', []):
                user_name = user['UserName']
                
                # Check for users without MFA
                mfa_devices = self.iam_client.list_mfa_devices(UserName=user_name)
                if not mfa_devices.get('MFADevices'):
                    misconfigs.append({
                        "resource": f"iam:user:{user_name}",
                        "type": "no_mfa",
                        "severity": "medium",
                        "description": f"User {user_name} does not have MFA enabled",
                        "recommendation": "Enable MFA for user"
                    })
                
                # Check for admin policies
                attached_policies = self.iam_client.list_attached_user_policies(UserName=user_name)
                for policy in attached_policies.get('AttachedPolicies', []):
                    if 'Admin' in policy['PolicyName'] or 'Administrator' in policy['PolicyName']:
                        misconfigs.append({
                            "resource": f"iam:user:{user_name}",
                            "type": "admin_policy",
                            "severity": "high",
                            "description": f"User {user_name} has admin policy attached",
                            "recommendation": "Review and restrict permissions using principle of least privilege"
                        })
        
        except Exception as e:
            self.logger.error(f"Error checking IAM misconfigs: {e}")
        
        return misconfigs
    
    def _check_ec2_misconfigs(self) -> List[Dict[str, Any]]:
        """Check EC2 security misconfigurations"""
        misconfigs = []
        
        # Simulated EC2 checks (LocalStack has limited EC2 support)
        misconfigs.append({
            "resource": "ec2:security-group:default",
            "type": "open_security_group",
            "severity": "high",
            "description": "Default security group allows all traffic",
            "recommendation": "Restrict security group rules"
        })
        
        return misconfigs
    
    def validate_iam_policy(self, policy_document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate IAM policy document
        
        Args:
            policy_document: IAM policy document (JSON)
        
        Returns:
            Validation results
        """
        self.logger.info("Validating IAM policy")
        
        issues = []
        warnings = []
        
        # Check for common misconfigurations
        statements = policy_document.get('Statement', [])
        
        for i, statement in enumerate(statements):
            # Check for wildcard actions
            actions = statement.get('Action', [])
            if isinstance(actions, list) and '*' in actions:
                issues.append({
                    "statement_index": i,
                    "type": "wildcard_action",
                    "severity": "high",
                    "description": "Policy contains wildcard action (*)",
                    "recommendation": "Use specific actions instead of wildcards"
                })
            
            # Check for wildcard resources
            resources = statement.get('Resource', [])
            if isinstance(resources, list) and '*' in resources:
                issues.append({
                    "statement_index": i,
                    "type": "wildcard_resource",
                    "severity": "high",
                    "description": "Policy contains wildcard resource (*)",
                    "recommendation": "Use specific resource ARNs"
                })
            
            # Check for missing conditions
            if 'Condition' not in statement and statement.get('Effect') == 'Allow':
                warnings.append({
                    "statement_index": i,
                    "type": "no_conditions",
                    "severity": "medium",
                    "description": "Allow statement has no conditions",
                    "recommendation": "Add conditions to restrict access"
                })
        
        # Try to validate with AWS IAM (if available)
        validation_result = None
        try:
            if self.iam_client:
                policy_json = json.dumps(policy_document)
                response = self.iam_client.simulate_principal_policy(
                    PolicySourceArn="arn:aws:iam::000000000000:user/test",
                    PolicyInputList=[policy_json]
                )
                validation_result = {
                    "aws_validation": "success",
                    "evaluation_results": len(response.get('EvaluationResults', []))
                }
        except Exception as e:
            self.logger.warning(f"AWS IAM validation not available: {e}")
            validation_result = {
                "aws_validation": "unavailable",
                "reason": str(e)
            }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "aws_validation": validation_result,
            "recommendations": self._generate_policy_recommendations(issues, warnings)
        }
    
    def analyze_request_logs(self, log_group: str = "/aws/lambda/self-healing-test-lambda", 
                           hours: int = 24) -> Dict[str, Any]:
        """
        Analyze CloudWatch request logs for security threats
        
        Args:
            log_group: CloudWatch log group name
            hours: Number of hours to analyze
        
        Returns:
            Analysis results with detected threats
        """
        self.logger.info(f"Analyzing request logs from {log_group}")
        
        threats = []
        anomalies = []
        
        try:
            # Get log streams
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Simulate log analysis (LocalStack CloudWatch has limited functionality)
            # In production, this would query actual CloudWatch logs
            
            # Simulated threat detection
            threats.append({
                "type": "brute_force",
                "severity": "high",
                "description": "Multiple failed authentication attempts detected",
                "source_ip": "192.168.1.100",
                "count": 15,
                "timestamp": (start_time + timedelta(hours=2)).isoformat()
            })
            
            anomalies.append({
                "type": "unusual_traffic_pattern",
                "severity": "medium",
                "description": "Unusual spike in request volume",
                "normal_rate": 100,
                "detected_rate": 500,
                "timestamp": (start_time + timedelta(hours=5)).isoformat()
            })
            
            # Check for suspicious patterns
            suspicious_patterns = self._detect_suspicious_patterns(log_group, start_time, end_time)
            threats.extend(suspicious_patterns)
        
        except Exception as e:
            self.logger.error(f"Error analyzing logs: {e}")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "log_group": log_group,
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "threats": threats,
            "anomalies": anomalies,
            "summary": {
                "total_threats": len(threats),
                "total_anomalies": len(anomalies),
                "high_severity": len([t for t in threats if t.get('severity') == 'high']),
                "medium_severity": len([t for t in threats if t.get('severity') == 'medium'])
            }
        }
    
    def _detect_suspicious_patterns(self, log_group: str, start_time: datetime, 
                                   end_time: datetime) -> List[Dict[str, Any]]:
        """Detect suspicious patterns in logs"""
        patterns = []
        
        # Simulated pattern detection
        patterns.append({
            "type": "sql_injection_attempt",
            "severity": "high",
            "description": "Potential SQL injection pattern detected in request",
            "pattern": "'; DROP TABLE",
            "timestamp": (start_time + timedelta(hours=3)).isoformat()
        })
        
        patterns.append({
            "type": "xss_attempt",
            "severity": "medium",
            "description": "Potential XSS attack pattern detected",
            "pattern": "<script>",
            "timestamp": (start_time + timedelta(hours=4)).isoformat()
        })
        
        return patterns
    
    def _calculate_severity_breakdown(self, misconfigs: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate severity breakdown"""
        breakdown = {"high": 0, "medium": 0, "low": 0}
        for misconfig in misconfigs:
            severity = misconfig.get("severity", "low")
            breakdown[severity] = breakdown.get(severity, 0) + 1
        return breakdown
    
    def _generate_policy_recommendations(self, issues: List[Dict], 
                                       warnings: List[Dict]) -> List[str]:
        """Generate policy improvement recommendations"""
        recommendations = []
        
        if any(i.get("type") == "wildcard_action" for i in issues):
            recommendations.append("Replace wildcard actions with specific permissions")
        
        if any(i.get("type") == "wildcard_resource" for i in issues):
            recommendations.append("Replace wildcard resources with specific ARNs")
        
        if warnings:
            recommendations.append("Add conditions to restrict access scope")
        
        if not recommendations:
            recommendations.append("Policy appears to follow security best practices")
        
        return recommendations


def main():
    """Test the CloudSecurityAdapter"""
    adapter = CloudSecurityAdapter()
    
    # Test security misconfiguration detection
    print("=== Security Misconfiguration Detection ===")
    misconfigs = adapter.detect_security_misconfig()
    print(json.dumps(misconfigs, indent=2))
    
    # Test IAM policy validation
    print("\n=== IAM Policy Validation ===")
    test_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*"
            }
        ]
    }
    validation = adapter.validate_iam_policy(test_policy)
    print(json.dumps(validation, indent=2))
    
    # Test request log analysis
    print("\n=== Request Log Analysis ===")
    log_analysis = adapter.analyze_request_logs()
    print(json.dumps(log_analysis, indent=2))


if __name__ == "__main__":
    main()

