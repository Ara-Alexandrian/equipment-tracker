# Developer Guide

This guide outlines best practices for developing and contributing to the GearVue project.

## Branch Management

### Core Principle: Never Commit Directly to Main

**IMPORTANT: The main branch should ALWAYS remain in a stable state.**

All development work must be done on feature or bugfix branches, not directly on the main branch. This ensures that the main branch is always in a deployable state and prevents accidental introduction of bugs or incomplete features.

### Branch Naming Conventions

Use descriptive, kebab-case names with appropriate prefixes:

- `feature/` - For new features (e.g., `feature/transport-system`)
- `bugfix/` - For bug fixes (e.g., `bugfix/modal-backdrop-issue`)
- `refactor/` - For code refactoring (e.g., `refactor/theme-system`)
- `docs/` - For documentation updates (e.g., `docs/update-theme-guide`)
- `test/` - For adding or updating tests (e.g., `test/checkout-validation`)

### Workflow

1. **Start from an updated main branch**
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes**
   - Implement your feature or fix
   - Commit regularly with descriptive messages
   - Keep changes focused on a single purpose

4. **Test your changes**
   - Run appropriate tests
   - Manually verify functionality

5. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a pull request**
   - Provide a clear description of your changes
   - Reference any relevant issues
   - Request reviews from appropriate team members

7. **Address review feedback**
   - Make requested changes
   - Push updates to your branch

8. **Merge to main**
   - Only after receiving approval
   - Use the "Squash and merge" option for cleaner history if multiple small commits were made

9. **Delete the branch**
   - After successful merge, delete the feature branch
   ```bash
   git branch -d feature/your-feature-name
   ```

## Commit Messages

Write clear, concise commit messages that explain:
- What changes were made
- Why the changes were needed (not just what was done)

Format:
```
Brief summary of changes (50 chars or less)

More detailed explanation, if necessary. Wrap at 72 characters.
Explain the problem that this commit is solving, and why this
approach was taken rather than alternatives.
```

## Code Style

Follow the established code style of the project:
- Use 4 spaces for indentation
- Group imports by standard library, third-party, and local modules
- Use appropriate docstrings for modules, classes, and functions
- Keep functions focused on a single task with descriptive names
- Use comments to explain "why" not "what"

## Pull Request Guidelines

When creating a pull request:
1. Provide a clear title and description
2. List the changes made and why they were needed
3. Include any steps to test the changes
4. Reference related issues using keywords like "Fixes #123" or "Relates to #456"
5. Request reviews from appropriate team members

## Testing

- Write tests for new features and bug fixes
- Run existing tests before submitting a pull request
- Make sure your changes don't break existing functionality

## Documentation

- Update documentation when you change code behavior
- Document new features with clear examples
- Keep the CHANGELOG.md updated with significant changes

## Troubleshooting

If you encounter issues:
1. Check for existing issues in the repository
2. Ask for help in the team communication channel
3. Document solutions for future reference

By following these guidelines, we can maintain a stable, high-quality codebase and collaborate effectively.