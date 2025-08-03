"""Simple code quality checker for the weather dashboard project"""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

class CodeQualityChecker:
    """Checks code quality and provides suggestions for improvement"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = []
    
    def check_wildcard_imports(self) -> List[str]:
        """Check for wildcard imports (from module import *)"""
        issues = []
        pattern = r'from\s+\w+\s+import\s+\*'
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if re.search(pattern, content):
                        issues.append(f"Wildcard import found in {py_file}")
            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")
        
        return issues
    
    def check_generic_exceptions(self) -> List[str]:
        """Check for generic exception handling (except Exception:)"""
        issues = []
        pattern = r'except\s+Exception\s*:'
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if re.search(pattern, line):
                            issues.append(f"Generic exception in {py_file}:{line_num}")
            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")
        
        return issues
    
    def check_large_files(self, max_lines: int = 500) -> List[str]:
        """Check for files that are too large"""
        issues = []
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
                    if line_count > max_lines:
                        issues.append(f"Large file: {py_file} ({line_count} lines)")
            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")
        
        return issues
    
    def check_missing_docstrings(self) -> List[str]:
        """Check for functions and classes without docstrings"""
        issues = []
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    # Check for class definitions
                    if re.match(r'^\s*class\s+\w+', line):
                        # Look for docstring in next few lines
                        has_docstring = False
                        for i in range(line_num, min(line_num + 5, len(lines))):
                            if '"""' in lines[i-1] or "'''" in lines[i-1]:
                                has_docstring = True
                                break
                        if not has_docstring:
                            issues.append(f"Class without docstring: {py_file}:{line_num}")
                    
                    # Check for function definitions
                    elif re.match(r'^\s*def\s+\w+', line):
                        # Look for docstring in next few lines
                        has_docstring = False
                        for i in range(line_num, min(line_num + 5, len(lines))):
                            if '"""' in lines[i-1] or "'''" in lines[i-1]:
                                has_docstring = True
                                break
                        if not has_docstring:
                            issues.append(f"Function without docstring: {py_file}:{line_num}")
                            
            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")
        
        return issues
    
    def run_all_checks(self) -> Dict[str, List[str]]:
        """Run all code quality checks"""
        results = {
            'wildcard_imports': self.check_wildcard_imports(),
            'generic_exceptions': self.check_generic_exceptions(),
            'large_files': self.check_large_files(),
            'missing_docstrings': self.check_missing_docstrings()
        }
        
        return results
    
    def print_report(self, results: Dict[str, List[str]]) -> None:
        """Print a formatted report of code quality issues"""
        print("=" * 60)
        print("CODE QUALITY REPORT")
        print("=" * 60)
        
        total_issues = 0
        for check_name, issues in results.items():
            print(f"\n{check_name.upper().replace('_', ' ')}:")
            if issues:
                for issue in issues:
                    print(f"  ❌ {issue}")
                total_issues += len(issues)
            else:
                print("  ✅ No issues found")
        
        print(f"\n{'=' * 60}")
        print(f"TOTAL ISSUES: {total_issues}")
        print("=" * 60)

def main():
    """Run code quality checks"""
    checker = CodeQualityChecker()
    results = checker.run_all_checks()
    checker.print_report(results)

if __name__ == "__main__":
    main() 