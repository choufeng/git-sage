        """Get Git repository for current directory"""
        """Get list of files that have been git added"""
            # Get modified files in staging area
                # For initial commit, get all staged files
                # Get all new files added to staging area
            return list(set(staged_files))  # Remove duplicates
        """Get changes in staged files"""
            # Get differences between staging area and HEAD
                # For initial repository, show content of files in staging area
        Commit changes
        :param message: Commit message
        :param confirm: Whether to require edit confirmation
        :return: Whether commit was successful
                # Create temporary file for editing commit message
                    temp_file.write("\n\n# Please edit your commit message above.")
                    temp_file.write("\n# Save and exit the editor to proceed with the commit.")
                    temp_file.write("\n# Interrupting the edit will cancel the commit.")
                    # Open temporary file with system default editor
                    # Read edited commit message
                    # Cancel commit only if message is empty
                        print("Commit message is empty, commit cancelled.")
                    # Ask user to confirm commit
                    confirm_input = input("\nConfirm commit? [Y/n] ").strip().lower()
                        # Execute commit
                        print("Commit completed.")
                        print("Commit cancelled.")
                    # Clean up temporary file
                # If no confirmation needed, commit directly
        """Check if there are staged changes"""
            # Use get_staged_files to check for staged files