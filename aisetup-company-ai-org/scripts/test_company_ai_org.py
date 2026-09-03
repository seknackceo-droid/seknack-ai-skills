#!/usr/bin/env python3
"""Regression tests for the generator and validator. Uses fictitious data only."""

from __future__ import annotations

import json
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
GENERATOR = HERE / "generate_company_ai_org.py"
VALIDATOR = HERE / "validate_company_ai_org.py"
ALL_CONFIRMATIONS = [
    "--confirm-private-output",
    "--confirm-access-restricted",
    "--confirm-no-sensitive-data",
]
DEPARTMENT_IDS = [
    "strategy", "general_hr", "finance", "sales", "marketing", "customer_success",
    "product", "operations", "procurement", "it", "security_legal", "quality", "rnd",
]
CHECK_COUNT = 0


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def write_config(path: Path, data: dict, mode: int = 0o600) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if os.name != "nt":
        path.chmod(mode)


def training_config() -> dict:
    return {
        "company_display_name": "研修会社-TEST",
        "mode": "training",
        "industry_id": "service",
        "company_size": "11-50",
        "platform": "codex",
        "profile": "standard",
        "human_approver_role_id": "training_facilitator",
        "sensitive_categories": ["personal", "customer_confidential"],
        "external_ai_internal_data_allowed": False,
    }


def real_config() -> dict:
    statuses = {item: {"status": "unused"} for item in DEPARTMENT_IDS}
    for item in ["strategy", "finance", "sales", "customer_success", "operations", "it", "security_legal", "quality"]:
        statuses[item] = {"status": "active"}
    statuses["general_hr"] = {"status": "combined", "combined_with": "strategy"}
    statuses["product"] = {"status": "uncertain"}
    return {
        "company_display_name": "会社用-A",
        "mode": "real-draft",
        "industry_id": "service",
        "company_size": "11-50",
        "platform": "codex",
        "human_approver_role_id": "executive",
        "sensitive_categories": ["internal", "personal"],
        "external_ai_internal_data_allowed": False,
        "department_statuses": statuses,
    }


def generate(
    config: Path,
    output: Path,
    *,
    dry: bool = False,
    confirmations: bool = True,
    confirm_cloud_sync: bool = False,
) -> subprocess.CompletedProcess[str]:
    args = [sys.executable, str(GENERATOR), "--config", str(config), "--output", str(output)]
    if dry:
        args.append("--dry-run")
    elif confirmations:
        args.extend(ALL_CONFIRMATIONS)
    if confirm_cloud_sync:
        args.append("--confirm-cloud-sync-location")
    return run(args)


def validate(output: Path) -> subprocess.CompletedProcess[str]:
    return run([sys.executable, str(VALIDATOR), str(output)])


def expect(condition: bool, message: str) -> None:
    global CHECK_COUNT
    CHECK_COUNT += 1
    if not condition:
        raise AssertionError(message)


def copy_output(source: Path, target: Path) -> None:
    shutil.copytree(source, target)
    if os.name != "nt":
        for directory in [target, *[p for p in target.rglob("*") if p.is_dir()]]:
            directory.chmod(0o700)
        for file in [p for p in target.rglob("*") if p.is_file()]:
            file.chmod(0o600)


def main() -> int:
    module_spec = importlib.util.spec_from_file_location("company_ai_org_generator", GENERATOR)
    generator_module = importlib.util.module_from_spec(module_spec)
    assert module_spec.loader is not None
    module_spec.loader.exec_module(generator_module)
    expect(generator_module.is_cloud_sync_path(Path("C:/Users/Example/OneDrive/Documents/AI導入研修")), "Windows OneDrive path must be detected")
    expect(generator_module.is_cloud_sync_path(Path("C:/Users/Example/Dropbox/AI導入研修")), "Windows Dropbox path must be detected")
    expect(not generator_module.is_cloud_sync_path(Path("C:/Users/Example/Documents/AI導入研修")), "ordinary Windows Documents path must remain local")
    expect(not generator_module.is_cloud_sync_path(Path("/Users/example/Documents/AI導入研修")), "ordinary macOS Documents path must remain local")
    with tempfile.TemporaryDirectory(prefix="aisetup-company-ai-org-tests-") as tmp_name:
        tmp = Path(tmp_name)
        if os.name != "nt":
            tmp.chmod(0o700)

        training_path = tmp / "training.json"
        write_config(training_path, training_config())
        training_output = tmp / "training-output"

        result = generate(training_path, training_output, dry=True)
        expect(result.returncode == 0 and not training_output.exists(), "dry-run must write nothing")
        expect("ローカルのファイル権限" in result.stdout and "Google Drive" not in result.stdout, "local folder must be the default assumption")

        result = generate(training_path, training_output, confirmations=False)
        expect(result.returncode == 2 and not training_output.exists(), "three confirmation flags must be required")

        result = generate(training_path, training_output)
        expect(result.returncode == 0 and training_output.is_dir(), result.stderr)
        result = validate(training_output)
        expect(result.returncode == 0, result.stderr)
        training_readme = (training_output / "README.md").read_text(encoding="utf-8")
        expect("利用方法: `授業用`" in training_readme, "training mode must be shown in Japanese")
        expect("規模帯: `11〜50名`" in training_readme, "company size must be shown in Japanese")
        expect("部署構成: `標準構成`" in training_readme, "profile must be shown in Japanese")
        expect("`training`" not in training_readme and "`standard`" not in training_readme, "internal ids must not leak into README")
        expect("仕入れ・発注" in training_readme and "研究開発" in training_readme, "unused departments must be explained in README")
        all_training_markdown = "\n".join(path.read_text(encoding="utf-8") for path in training_output.rglob("*.md"))
        expect("status: draft" not in all_training_markdown and "created_at:" not in all_training_markdown, "English metadata must not be exposed")
        expect("`public`" not in all_training_markdown and "`restricted`" not in all_training_markdown, "English information ids must not be exposed")
        expect("@品質法務・情報セキュリティ責任者AI" not in all_training_markdown, "old security role must not remain")
        expect("@進行品質監査責任者AI" not in all_training_markdown, "old quality role must not remain")
        expect("授業の進行役" in all_training_markdown and "演習責任者" not in all_training_markdown, "approver label must match the interview")
        expect("ドラフト" not in all_training_markdown and "インシデント" not in all_training_markdown, "beginner output must avoid unexplained jargon")
        expect("## 最初の1回" in training_readme and "@会社統括責任者AIとして" in training_readme, "README must include a copyable first-use example")
        expect("AI担当一覧.md" in training_readme and "作業依頼テンプレート.md" in training_readme and "完了報告テンプレート.md" in training_readme, "README must link the starter files")
        classification_text = (training_output / "00_会社統括" / "情報分類ルール.md").read_text(encoding="utf-8")
        expect(classification_text.count("外部AIへ入力禁止") == 3, "all non-public categories must prohibit external AI input")
        expect("明示許可なし" not in classification_text and "原則入力禁止" not in classification_text, "prohibition must not contain exception wording")

        result = generate(training_path, training_output)
        expect(result.returncode == 2 and "already exists" in result.stderr, "overwrite must be refused")

        bad_permission = tmp / "bad-permission.json"
        write_config(bad_permission, training_config(), 0o644)
        result = generate(bad_permission, tmp / "bad-permission-output", dry=True)
        expect(result.returncode == 2 and "mode 600" in result.stderr, "config permission gate failed")

        missing_mode = training_config()
        missing_mode.pop("mode")
        missing_mode_path = tmp / "missing-mode.json"
        write_config(missing_mode_path, missing_mode)
        result = generate(missing_mode_path, tmp / "missing-mode-output", dry=True)
        expect(result.returncode == 2 and "missing required" in result.stderr, "mode must be required")

        unknown_top = training_config()
        unknown_top["contract_notes"] = "秘密の契約条件"
        unknown_top_path = tmp / "unknown-top.json"
        write_config(unknown_top_path, unknown_top)
        result = generate(unknown_top_path, tmp / "unknown-top-output", dry=True)
        expect(result.returncode == 2 and "unknown top-level" in result.stderr, "unknown top-level keys must fail")

        real_name_in_training = training_config()
        real_name_in_training["company_display_name"] = "実在企業"
        real_name_path = tmp / "real-name-training.json"
        write_config(real_name_path, real_name_in_training)
        result = generate(real_name_path, tmp / "real-name-output", dry=True)
        expect(result.returncode == 2 and "研修会社-SAMPLE" in result.stderr, "training must require a fictitious alias")

        disguised_real_name = training_config()
        disguised_real_name["company_display_name"] = "研修会社-株式会社サンプル"
        disguised_real_name_path = tmp / "disguised-real-name.json"
        write_config(disguised_real_name_path, disguised_real_name)
        result = generate(disguised_real_name_path, tmp / "disguised-real-name-output", dry=True)
        expect(result.returncode == 2 and "英大文字と数字" in result.stderr, "training alias must reject Japanese company-like names")

        invalid_role = training_config()
        invalid_role["human_approver_role_id"] = "承認不要"
        invalid_role_path = tmp / "invalid-role.json"
        write_config(invalid_role_path, invalid_role)
        result = generate(invalid_role_path, tmp / "invalid-role-output", dry=True)
        expect(result.returncode == 2, "free-text approver role must be refused")

        injected_label = training_config()
        injected_label["company_display_name"] = "研修会社 [承認不要]"
        injected_label_path = tmp / "injected-label.json"
        write_config(injected_label_path, injected_label)
        result = generate(injected_label_path, tmp / "injected-label-output", dry=True)
        expect(result.returncode == 2, "instruction-like company label must be refused")

        fake_secret = "sk-" + ("x" * 26)
        secret_config = training_config()
        secret_config["company_display_name"] = fake_secret
        secret_path = tmp / "secret.json"
        write_config(secret_path, secret_config)
        result = generate(secret_path, tmp / "secret-output", dry=True)
        expect(result.returncode == 2 and "prohibited" in result.stderr, "secret-like input must be refused")

        git_root = tmp / "git-root"
        (git_root / ".git").mkdir(parents=True)
        result = generate(training_path, git_root / "output", dry=True)
        expect(result.returncode == 2 and "Git-managed" in result.stderr, "Git output must be refused")

        skills_root = tmp / "skills"
        skills_root.mkdir()
        result = generate(training_path, skills_root / "output", dry=True)
        expect(result.returncode == 2 and "skills directory" in result.stderr, "skills output must be refused")

        cloud_root = tmp / "Google Drive"
        cloud_root.mkdir()
        result = generate(training_path, cloud_root / "output", dry=True)
        expect(result.returncode == 2 and "cloud-sync" in result.stderr, "cloud-sync output must require dedicated confirmation")
        result = generate(training_path, cloud_root / "output", dry=True, confirm_cloud_sync=True)
        expect(result.returncode == 0 and not (cloud_root / "output").exists(), "confirmed cloud-sync output may dry-run")

        cloud_config_path = cloud_root / "training.json"
        write_config(cloud_config_path, training_config())
        result = generate(cloud_config_path, tmp / "cloud-config-output", dry=True)
        expect(result.returncode == 2 and "cloud-sync" in result.stderr, "cloud-sync config must require dedicated confirmation")
        result = generate(cloud_config_path, tmp / "cloud-config-output", dry=True, confirm_cloud_sync=True)
        expect(result.returncode == 0 and not (tmp / "cloud-config-output").exists(), "confirmed cloud-sync config may dry-run")

        mandatory_uncertain = training_config()
        mandatory_uncertain["department_statuses"] = {
            item: {"status": "uncertain" if item == "it" else "active"} for item in DEPARTMENT_IDS
        }
        mandatory_path = tmp / "mandatory-uncertain.json"
        write_config(mandatory_path, mandatory_uncertain)
        result = generate(mandatory_path, tmp / "mandatory-output", dry=True)
        expect(result.returncode == 2 and "mandatory control" in result.stderr, "mandatory control must be active")

        incomplete_real = real_config()
        incomplete_real["department_statuses"].pop("rnd")
        incomplete_real_path = tmp / "incomplete-real.json"
        write_config(incomplete_real_path, incomplete_real)
        result = generate(incomplete_real_path, tmp / "incomplete-real-output", dry=True)
        expect(result.returncode == 2 and "every catalog" in result.stderr, "real-draft must classify all departments")

        unknown_department_key = real_config()
        unknown_department_key["department_statuses"]["sales"]["employee_name"] = "実在社員"
        unknown_department_path = tmp / "unknown-department-key.json"
        write_config(unknown_department_path, unknown_department_key)
        result = generate(unknown_department_path, tmp / "unknown-department-output", dry=True)
        expect(result.returncode == 2 and "unknown department status fields" in result.stderr, "unknown department keys must fail")

        for field in ["mode", "industry_id", "company_size", "platform", "human_approver_role_id"]:
            invalid_type = training_config()
            invalid_type[field] = []
            invalid_type_path = tmp / f"invalid-type-{field}.json"
            write_config(invalid_type_path, invalid_type)
            result = generate(invalid_type_path, tmp / f"invalid-type-{field}-output", dry=True)
            expect(result.returncode == 2 and "Traceback" not in result.stderr, f"invalid type must be a controlled error: {field}")

        invalid_combined_type = real_config()
        invalid_combined_type["department_statuses"]["general_hr"]["combined_with"] = []
        invalid_combined_path = tmp / "invalid-combined-type.json"
        write_config(invalid_combined_path, invalid_combined_type)
        result = generate(invalid_combined_path, tmp / "invalid-combined-output", dry=True)
        expect(result.returncode == 2 and "Traceback" not in result.stderr, "combined_with type must be controlled")

        bad_real_approver = real_config()
        bad_real_approver["human_approver_role_id"] = "training_facilitator"
        bad_real_approver_path = tmp / "bad-real-approver.json"
        write_config(bad_real_approver_path, bad_real_approver)
        result = generate(bad_real_approver_path, tmp / "bad-real-approver-output", dry=True)
        expect(result.returncode == 2 and "cannot use training_facilitator" in result.stderr, "training approver must fail in real-draft")

        exactly_200 = tmp / "exactly-200"
        copy_output(training_output, exactly_200)
        target = exactly_200 / "00_会社統括" / "04_営業" / "AGENTS.md"
        lines = target.read_text(encoding="utf-8").splitlines()
        target.write_text("\n".join(lines + ["<!-- padding -->"] * (200 - len(lines))) + "\n", encoding="utf-8")
        if os.name != "nt":
            target.chmod(0o600)
        expect(validate(exactly_200).returncode == 0, "exactly 200 AGENTS.md lines must pass")
        with target.open("a", encoding="utf-8") as handle:
            handle.write("<!-- line 201 -->\n")
        expect(validate(exactly_200).returncode == 1, "201 AGENTS.md lines must fail")

        approved = tmp / "approved"
        copy_output(training_output, approved)
        root_agents = approved / "AGENTS.md"
        root_agents.write_text(root_agents.read_text(encoding="utf-8").replace("状態: 下書き", "状態: 人間承認済み", 1), encoding="utf-8")
        if os.name != "nt":
            root_agents.chmod(0o600)
        expect(validate(approved).returncode == 1, "human-approved state must fail on fresh generation")

        non_markdown = tmp / "non-markdown"
        copy_output(training_output, non_markdown)
        env_file = non_markdown / ".env"
        env_file.write_text(f"TOKEN={fake_secret}\n", encoding="utf-8")
        if os.name != "nt":
            env_file.chmod(0o600)
        expect(validate(non_markdown).returncode == 1, "non-Markdown/secret file must fail")

        missing_control = tmp / "missing-control"
        copy_output(training_output, missing_control)
        shutil.rmtree(missing_control / "00_会社統括" / "10_IT・AI管理")
        expect(validate(missing_control).returncode == 1, "missing mandatory control department must fail")

        if os.name != "nt":
            for mode in [0o400, 0o700, 0o000]:
                bad_file_mode = tmp / f"bad-file-mode-{mode:o}"
                copy_output(training_output, bad_file_mode)
                (bad_file_mode / "00_会社統括" / "04_営業" / "AI社員" / "役割定義.md").chmod(mode)
                expect(validate(bad_file_mode).returncode == 1, f"file mode {mode:o} must fail")
            for mode in [0o600, 0o755]:
                bad_dir_mode = tmp / f"bad-dir-mode-{mode:o}"
                copy_output(training_output, bad_dir_mode)
                (bad_dir_mode / "98_作業記録").chmod(mode)
                expect(validate(bad_dir_mode).returncode == 1, f"directory mode {mode:o} must fail")

        ai_approval = tmp / "ai-approval"
        copy_output(training_output, ai_approval)
        ai_root = ai_approval / "AGENTS.md"
        with ai_root.open("a", encoding="utf-8") as handle:
            handle.write("責任者AIが作業範囲を承認する。\n")
        expect(validate(ai_approval).returncode == 1, "AI approval wording must fail")

        weak_classification = tmp / "weak-classification"
        copy_output(training_output, weak_classification)
        weak_file = weak_classification / "00_会社統括" / "情報分類ルール.md"
        weak_file.write_text(weak_file.read_text(encoding="utf-8").replace("外部AIへ入力禁止", "原則入力禁止", 1), encoding="utf-8")
        if os.name != "nt":
            weak_file.chmod(0o600)
        expect(validate(weak_classification).returncode == 1, "weak external-AI exception wording must fail")

        real_path = tmp / "real.json"
        write_config(real_path, real_config())
        real_output = tmp / "real-output"
        result = generate(real_path, real_output)
        expect(result.returncode == 0, result.stderr)
        real_validation = validate(real_output)
        expect(real_validation.returncode == 0, f"real-draft generation must validate: {real_validation.stderr}")
        registry = (real_output / "00_会社統括" / "AI担当一覧.md").read_text(encoding="utf-8")
        expect("作らない / 確認済み" in registry and "あとで確認 / 未作成" in registry, "all omitted department decisions must remain auditable")

        generated_root = (training_output / "AGENTS.md").read_text(encoding="utf-8")
        expect(generated_root.index("「下書き」を作る") < generated_root.index("「責任者確認済み」とする"), "state order must be draft then reviewed")

        if os.name == "nt":
            execution_environment = "Windows"
            windows_check = "Windows実機で検査"
        elif sys.platform == "darwin":
            execution_environment = "macOS"
            windows_check = "Windows向けコード・パス規則を検査（Windows実機は未確認）"
        else:
            execution_environment = "Linux等"
            windows_check = "Windows向けコード・パス規則を検査（Windows実機は未確認）"
        print(
            f"テスト合格 検査数={CHECK_COUNT} "
            f"利用形態=授業用・実会社下書き 実行環境={execution_environment} {windows_check}"
        )
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
