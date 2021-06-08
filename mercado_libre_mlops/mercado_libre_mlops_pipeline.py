from aws_cdk import (core, aws_codebuild as codebuild,
                     aws_codepipeline as codepipeline,
                     aws_codepipeline_actions as codepipeline_actions)
import os

class MercadoLibreMlopsPipeline(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.owner = os.environ['owner']

        self.oauth_token  = core.SecretValue.secrets_manager(
            'personal/github',
            json_field='key',
        )

        self.cdk_build = codebuild.PipelineProject(self, "CdkBuild",
                        build_spec=codebuild.BuildSpec.from_object(dict(
                            version="0.2",
                            phases=dict(
                                install=dict(
                                    runtime_versions=dict(python="3.8"),
                                    commands=[
                                        "python -m pip install -r requirements.txt -q",
                                        "npm install aws-cdk -g",
                                        "npm update"
                                    ]),
                                build=dict(commands=[
                                    "npx cdk synth mercado-libre-mlops > template.yml"])),
                            artifacts={
                                "files": '**/*'},
                            environment=dict(buildImage=
                                codebuild.LinuxBuildImage.STANDARD_2_0))))

        self.source_output = codepipeline.Artifact()
        self.cdk_build_output = codepipeline.Artifact("CdkBuildOutput")


        codepipeline.Pipeline(self, "Pipeline",
            stages=[
                codepipeline.StageProps(stage_name="Source",
                    actions=[
                        codepipeline_actions.GitHubSourceAction(
                            action_name="GitHub_Source",
                            oauth_token = self.oauth_token,
                            repo="mercado-livre-mlops",
                            branch="main",
                            owner=self.owner,
                            output=self.source_output)]),
                codepipeline.StageProps(stage_name="Build",
                    actions=[
                        codepipeline_actions.CodeBuildAction(
                            action_name="CDK_Build",
                            project=self.cdk_build,
                            input=self.source_output,
                            outputs=[self.cdk_build_output])]),
                codepipeline.StageProps(stage_name="Deploy",
                    actions=[
                        codepipeline_actions.CloudFormationCreateUpdateStackAction(
                            action_name="CFN_Deploy",
                            template_path=self.cdk_build_output.at_path(
                                "MercadoLibreMlopsStack.template.json"),
                            stack_name="mercado-libre-mlops",
                            admin_permissions=True)])
                ]
            )